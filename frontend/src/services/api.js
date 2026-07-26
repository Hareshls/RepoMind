/**
 * API Service for RepoMind Backend
 */

export async function analyzeRepositoryAPI(repoUrl) {
  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_url: repoUrl })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Analysis request failed');
    }
    return data;
  } catch (error) {
    console.error('[API] analyzeRepositoryAPI Error:', error);
    throw error;
  }
}

export async function askQuestionAPI(question, repoUrl) {
  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question, repo_url: repoUrl })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Question request failed');
    }
    return data;
  } catch (error) {
    console.error('[API] askQuestionAPI Error:', error);
    throw error;
  }
}

export async function fetchRepositoriesAPI() {
  try {
    const response = await fetch('/repositories');
    if (!response.ok) return { repositories: [] };
    return await response.json();
  } catch (error) {
    console.error('[API] fetchRepositoriesAPI Error:', error);
    return { repositories: [] };
  }
}

