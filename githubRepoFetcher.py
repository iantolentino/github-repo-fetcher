import requests
import json
from typing import Dict, List, Optional
import time
import sys

class GitHubRepoFetcher:
    def __init__(self, token: str = None):
        """
        Initialize the GitHub repo fetcher
        
        Args:
            token: GitHub personal access token
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Repo-Fetcher"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def search_users(self, query: str) -> List[Dict]:
        """
        Search for GitHub users by username or name
        """
        url = f"{self.base_url}/search/users"
        params = {"q": query, "per_page": 10}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching users: {e}")
            return []
    
    def get_user_repos(self, username: str) -> List[Dict]:
        """
        Get all repositories for a specific user
        """
        url = f"{self.base_url}/users/{username}/repos"
        params = {"per_page": 100, "sort": "updated"}
        repos = []
        page = 1
        
        while True:
            params["page"] = page
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                page_repos = response.json()
                if not page_repos:
                    break
                    
                repos.extend(page_repos)
                
                # Check if there are more pages
                if 'next' not in response.links:
                    break
                    
                page += 1
                time.sleep(0.1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories: {e}")
                break
        
        return repos
    
    def get_repo_languages(self, username: str, repo_name: str) -> List[str]:
        """
        Get programming languages used in a repository
        """
        url = f"{self.base_url}/repos/{username}/{repo_name}/languages"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            languages_data = response.json()
            return list(languages_data.keys())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching languages for {repo_name}: {e}")
            return []
    
    def display_user_selection(self, users: List[Dict]) -> Optional[str]:
        """
        Display user search results and let user select one
        """
        if not users:
            print("No users found!")
            return None
        
        print("\n🔍 Search Results:")
        print("-" * 50)
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['login']} - {user.get('name', 'N/A')}")
            if user.get('bio'):
                print(f"   📝 {user['bio'][:80]}...")
            print(f"   👤 Followers: {user.get('followers', 0)} | Public Repos: {user.get('public_repos', 0)}")
            print()
        
        while True:
            try:
                choice = input("Select a user (number) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(users):
                    return users[choice_num - 1]['login']
                else:
                    print(f"Please enter a number between 1 and {len(users)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
    
    def display_repos(self, repos: List[Dict], username: str):
        """
        Display repositories with their details
        """
        if not repos:
            print(f"\nNo repositories found for user '{username}'")
            return
        
        print(f"\n📂 Repositories for {username} ({len(repos)} found)")
        print("=" * 80)
        
        for i, repo in enumerate(repos, 1):
            print(f"\n{i}. {repo['name']}")
            print(f"   📖 Description: {repo.get('description', 'No description')}")
            print(f"   🌟 Stars: {repo.get('stargazers_count', 0)}")
            print(f"   🍴 Forks: {repo.get('forks_count', 0)}")
            print(f"   📅 Updated: {repo.get('updated_at', 'N/A')[:10]}")
            print(f"   🔗 URL: {repo.get('html_url', 'N/A')}")
            
            # Get languages
            languages = self.get_repo_languages(username, repo['name'])
            if languages:
                print(f"   💻 Technologies: {', '.join(languages)}")
            else:
                print(f"   💻 Technologies: Not available")
            
            # Additional info
            if repo.get('language'):
                print(f"   🎯 Primary Language: {repo['language']}")
            
            if repo.get('has_issues'):
                print(f"   🐛 Issues: {repo.get('open_issues_count', 0)} open")
            
            if repo.get('license'):
                print(f"   📜 License: {repo['license'].get('name', 'N/A')}")
            
            print("-" * 60)
    
    def export_to_json(self, repos: List[Dict], username: str, filename: str = None):
        """
        Export repository data to JSON file
        """
        if not filename:
            filename = f"{username}_repositories.json"
        
        export_data = {
            "username": username,
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_repositories": len(repos),
            "repositories": []
        }
        
        for repo in repos:
            repo_data = {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "updated_at": repo.get("updated_at"),
                "primary_language": repo.get("language"),
                "languages": self.get_repo_languages(username, repo["name"]),
                "has_issues": repo.get("has_issues"),
                "open_issues": repo.get("open_issues_count"),
                "license": repo.get("license", {}).get("name") if repo.get("license") else None
            }
            export_data["repositories"].append(repo_data)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Data exported to {filename}")
        except Exception as e:
            print(f"Error exporting data: {e}")
    
    def run(self):
        """
        Main program loop
        """
        print("🚀 GitHub Repository Fetcher")
        print("=" * 50)
        print("✅ Using authenticated requests (5000 requests/hour)")
        
        while True:
            print("\nOptions:")
            print("1. Search for GitHub user")
            print("2. Exit")
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                self.search_and_display()
            elif choice == "2":
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def search_and_display(self):
        """
        Handle the search and display flow
        """
        search_query = input("\nEnter GitHub username or name to search: ").strip()
        if not search_query:
            print("Please enter a search query.")
            return
        
        print("🔍 Searching for users...")
        users = self.search_users(search_query)
        
        username = self.display_user_selection(users)
        if not username:
            return
        
        print(f"\n📥 Fetching repositories for {username}...")
        repos = self.get_user_repos(username)
        
        if repos:
            self.display_repos(repos, username)
            
            # Export option
            export_choice = input("\n💾 Export to JSON file? (y/n): ").strip().lower()
            if export_choice in ['y', 'yes']:
                filename = input("Enter filename (or press Enter for default): ").strip()
                self.export_to_json(repos, username, filename if filename else None)
        else:
            print(f"No repositories found for user '{username}'")


def main():
    """
    Main function with your token integrated
    """
    # Your GitHub token directly integrated
    
    fetcher = GitHubRepoFetcher(token=token)
    fetcher.run()


if __name__ == "__main__":
    main()
