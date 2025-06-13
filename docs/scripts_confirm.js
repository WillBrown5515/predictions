// Initialize Supabase client
const supabaseUrl = 'https://lcfqseitghkcxzjtamoz.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxjZnFzZWl0Z2hrY3h6anRhbW96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxNzIzNzAsImV4cCI6MjA2Mzc0ODM3MH0.kPuKlk_UXlcF4WFGdh8o4Kl792B93-Q7q9Z8oFtK9Mk';
const supaclient = supabase.createClient(supabaseUrl, supabaseAnonKey);

// DOM element for status
const statusEl = document.getElementById('status');

// delay function
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Main logic
async function handleConfirmation() {
  const { data: { user }, error } = await supaclient.auth.getUser();

  await delay(5000);

  if (error || !user) {
    statusEl.textContent = 'Could not confirm email. Please try logging in again.';
    return;
  }

  const id = user.id;
  const uname = user.user_metadata.username;

  statusEl.textContent = 'Email confirmed! Setting up your account...';

  await user_team_list(id, uname);
}

// return back to the main predictions page
async function returnHome() {
  statusEl.textContent = 'Redirecting...';
  setTimeout(() => {
    window.location.href = '/predictions/';
  }, 3000);
}

// When the user has registered, team list to be created
async function user_team_list(id, uname) {

  const league_shorthands = ['prem', 'la_liga', 'champ', 'seriea', 'bundes', 'ligue1']

  // Define how many teams are in each league
  const leagueTeamCounts = {
    prem: 20,
    champ: 24,
    la_liga: 20,
    seriea: 20,
    bundes: 18,
    ligue1: 18
  };

  for (let league of league_shorthands) {
    const teamCount = leagueTeamCounts[league];

    // Get team names from default_predictions
    const { data, error: fetchError } = await supaclient
      .from("default_predictions")
      .select("*")
      .eq("name", `${league}_all_teams`);

    if (fetchError) {
      console.error(`Error fetching default_predictions for ${league}:`, fetchError.message);
      continue;
    }

  const teamRow = { user_id: id };
  for (let i = 1; i <= teamCount; i++) {
    const key = i.toString();
    teamRow[key] = data[0][key] ?? null;
  }

   const {error: predInsertError} = await supaclient
    .from(`${league}_preds`)
    .insert([teamRow])
    .select();

    if (predInsertError) {
      console.error(`Error inserting into ${league}_preds:`, predInsertError.message);
    }

    // Insert default scores (all 0s)
    const updateData = {};
    for (let i = 1; i <= teamCount; i++) {
      updateData[i.toString()] = 0;
    }
    updateData.user_id = id;

    const { error: scoreInsertError } = await supaclient
      .from(`${league}_scores`)
      .insert([updateData]);

    if (scoreInsertError) {
      console.error(`Error inserting into ${league}_scores:`, scoreInsertError.message);
    }
  }

  // Add to leaderboard
  const { error: leaderboardInsertError } = await supaclient
    .from("leaderboard")
    .insert([{ 'username': uname, 'user_id': id }]);

  if (leaderboardInsertError) {
    console.error("Error inserting into leaderboard:", leaderboardInsertError.message);
  }
}

// Start when DOM is loaded
window.addEventListener('DOMContentLoaded', handleConfirmation);