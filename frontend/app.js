const API_BASE = "http://localhost:7072/api";

const serviceStatus = document.getElementById("serviceStatus");
const statusDot = document.getElementById("statusDot");
const greetingForm = document.getElementById("greetingForm");
const profileForm = document.getElementById("profileForm");
const greetingResult = document.getElementById("greetingResult");
const profileMessage = document.getElementById("profileMessage");
const profilesList = document.getElementById("profilesList");
const refreshProfiles = document.getElementById("refreshProfiles");

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    serviceStatus.textContent = data.status === "healthy" ? "Healthy" : "Unknown";
    statusDot.style.background = data.status === "healthy" ? "#22c55e" : "#f59e0b";
  } catch (error) {
    serviceStatus.textContent = "Backend offline";
    statusDot.style.background = "#ef4444";
  }
}

function renderResult(element, text, isSuccess = false) {
  element.classList.remove("empty");
  element.classList.toggle("success", isSuccess);
  element.textContent = text;
}

async function callGreeting(event) {
  event.preventDefault();
  const formData = new FormData(greetingForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch(`${API_BASE}/http_trigger`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    renderResult(
      greetingResult,
      `${data.message}\n\n${data.profile ? data.profile.summary : ""}`,
      response.ok,
    );
  } catch (error) {
    renderResult(greetingResult, "The greeting service is unavailable. Please check the local backend.", false);
  }
}

async function createProfile(event) {
  event.preventDefault();
  const formData = new FormData(profileForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch(`${API_BASE}/profiles`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    const success = response.ok && data.profile;
    renderResult(
      profileMessage,
      success ? `Profile created for ${data.profile.name}.` : data.message || "Profile creation failed.",
      success,
    );
    profileForm.reset();
    await loadProfiles();
  } catch (error) {
    renderResult(profileMessage, "Profile creation failed. Please verify the backend is running.", false);
  }
}

async function loadProfiles() {
  try {
    const response = await fetch(`${API_BASE}/profiles`);
    const data = await response.json();

    if (!Array.isArray(data.profiles) || data.profiles.length === 0) {
      profilesList.innerHTML = '<p class="empty-state">No profiles yet. Create one to get started.</p>';
      return;
    }

    profilesList.innerHTML = data.profiles
      .map(
        (profile) => `
          <article class="profile-card">
            <h3>${profile.name}</h3>
            <div class="profile-meta">${profile.city || "Unknown city"} • ${profile.language || "English"}</div>
            <div class="profile-meta">Interests: ${profile.interests ? profile.interests.join(", ") : "Not specified"}</div>
            <div class="profile-actions">
              <button type="button" data-profile-id="${profile.id}" data-action="delete">Delete</button>
            </div>
          </article>
        `,
      )
      .join("");

    profilesList.querySelectorAll("[data-action='delete']").forEach((button) => {
      button.addEventListener("click", async () => {
        const profileId = button.getAttribute("data-profile-id");
        await deleteProfile(profileId);
      });
    });
  } catch (error) {
    profilesList.innerHTML = '<p class="empty-state">Unable to load profiles.</p>';
  }
}

async function deleteProfile(profileId) {
  try {
    const response = await fetch(`${API_BASE}/profile/${profileId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      renderResult(profileMessage, `Profile ${profileId} was deleted.`, true);
      await loadProfiles();
      return;
    }

    const data = await response.json();
    renderResult(profileMessage, data.message || "Delete request failed.", false);
  } catch (error) {
    renderResult(profileMessage, "Delete request failed.", false);
  }
}

greetingForm.addEventListener("submit", callGreeting);
profileForm.addEventListener("submit", createProfile);
refreshProfiles.addEventListener("click", loadProfiles);

checkHealth();
loadProfiles();
