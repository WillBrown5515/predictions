const supaclient = supabase.createClient("https://pssnuzrmazyxouoqsfhg.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzc251enJtYXp5eG91b3FzZmhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExOTMyMjQsImV4cCI6MjA2Njc2OTIyNH0.4Vj8_1Yr6yc0KZadbdknBv548dr3_WXYfGmerswF3XY");

window.addEventListener('DOMContentLoaded', async () => {
  const params = new URLSearchParams(window.location.hash.slice(1));
  const access_token = params.get("access_token");
  const refresh_token = params.get("refresh_token");
  const type = params.get("type");

  const statusMessage = document.getElementById("statusMessage");

  if (access_token && refresh_token && type === "recovery") {
    // Set session so user is temporarily logged in
    const { error } = await supaclient.auth.setSession({
      access_token,
      refresh_token
    });

    if (error) {
      statusMessage.innerHTML = `<div class="alert alert-danger">Failed to authenticate reset link: ${error.message}</div>`;
      return;
    }

    // Show form
    document.getElementById("resetForm").classList.remove("d-none");
  } else {
    statusMessage.innerHTML = `<div class="alert alert-warning">Invalid or missing password reset token.</div>`;
  }
});

async function submitNewPassword() {
  const newPassword = document.getElementById("newPassword").value;
  const statusMessage = document.getElementById("statusMessage");

  if (!newPassword || newPassword.length < 6) {
    statusMessage.innerHTML = `<div class="alert alert-warning">Password must be at least 6 characters.</div>`;
    return;
  }

  const { error } = await supaclient.auth.updateUser({ password: newPassword });

  if (error) {
    statusMessage.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
  } else {
    statusMessage.innerHTML = `
    <div class="alert alert-success">
        Password updated successfully!
    </div>
    <a href="https://beat-the-bookie.github.io/predictor/" class="btn btn-primary mt-3">Return to Login</a>
    `;
    document.getElementById("resetForm").classList.add("d-none");
  }
}
