export async function fetchPublicGitHubEvents(username, lastEventTime) {
  try {
    const response = await fetch(`https://api.github.com/users/${username}/events/public`);
    if (!response.ok) {
      throw new Error('Failed to fetch GitHub events');
    }
    const events = await response.json();

    // Filter out events older than the last event time
    const newEvents = events.filter(event => new Date(event.created_at) > new Date(lastEventTime));

    return newEvents;
  } catch (error) {
    console.error('Error fetching GitHub events:', error);
    return [];
  }
}
