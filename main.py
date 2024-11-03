import re

# Required Classes are imported from other files
from social_network import SocialNetwork
from hobby_network import HobbyNetwork
from friend_recommendation import FriendRecommender
from auto_complete import Trie

# Imported Classes are initialised
network = SocialNetwork()
hobby_network = HobbyNetwork()
recommender = FriendRecommender(network, hobby_network)
trie = Trie()

def validate_username(username):
    """
    Function to validate username using RegEx
    """
    return re.match(r'^[A-Za-z0-9_.]+$', username) # Allows only alphabets, digits, underscores and periods

def confirm_username(username, suggestions):
    """
     Function that returns the desired username from the recieved suggestions
    """
    # If only 1 partial match is found
    if len(suggestions) == 1 and suggestions[0] != username.lower(): 
            confirmation = input(f"Similar username found. Did you mean {suggestions[0]}? (yes/no): ")
            if confirmation.lower() in {"y", "yes"}: # If confirmation yields yes, return it, else return None for repeat
                return suggestions[0]
    else: # If more than 1 partial match was found
        print("Similar usernames found:")
        for i, suggestion in enumerate(suggestions, start=1):
            print(f"{i}. {suggestion}") # Print the matches for user to decide
        print("0. Retry")
        while True:
            try:
                confirmation = int(input("Select intended username >> "))
                if confirmation == 0:
                    break
                elif 1 <= confirmation <= len(suggestions):
                    return suggestions[confirmation - 1] # Return the desired username
                else:
                    print("Invalid option. Please try again!")
            except ValueError:
                print("Invalid option. Please enter a number!")
    return None # If no desired username was chosen, return None for repeat

def get_username(input_msg, current_username=None):
    """
    Function to handle the process of getting the desired username
    """
    while True:
        username = input(input_msg)
        # Searches if exact input has a match in Trie, if not it gets suggestions/close matches
        if not trie.search(username): 
            suggestions = trie.get_suggestions(username)
            # Remove the current username from suggestions, so that you can't search yourself
            if current_username in suggestions: 
                suggestions.remove(current_username)
            if not suggestions: # If suggestions returns [], it means no matches
                print("No such username found! Please try again.")
                continue
            confirmed_username = confirm_username(username, suggestions) # Gets desried username from function 
        else:
            confirmed_username = username # If input's exact match is there, set that as desired username for return
        if confirmed_username: # If desired username is got, return it, else repeat
            return confirmed_username
        
def display_post(post):
    """
    Function to display details of a post. (Designed to remove repeated code)
    """
    print("-----------------------------------------------------------------------------------")
    print(post)
    print("Liked by:", ", ".join(post.likes) if post.likes else "No likes yet") # Print Like Details
    if post.comments: # If post.comments exist, print the comment details
        print("\nComments:")
        for commenter, comment, timestamp in post.comments:
            print(f"  {commenter} ({timestamp.strftime('%Y-%m-%d %H:%M')}): {comment}")

def handle_post_menu(network, username):
    while True:
        print("\n==== Post Menu ====")
        print("1. Create New Post")
        print("2. View My Posts")
        print("3. View Friend Posts")
        print("4. Like/Unlike Post")
        print("5. Comment on Post")
        print("6. Back to Main Menu")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            content = input("Enter your post content: ")
            post_id = network.create_post(username, content)
            print("Post created successfully!")
            
        elif choice == "2":
            posts = network.get_user_posts(username)
            if posts:
                print("\nYour Posts:")
                for pid, post in posts:
                    print(f"\nPost ID: {pid}")
                    display_post(post)
            else:
                print("No posts yet!")
                
        elif choice == "3":
            posts = network.get_personalized_feed(username)
            if posts:
                print("\nFriend Posts:")
                for post in posts:
                    print(f"\nPost ID: {post.pid}")
                    display_post(post)
            else:
                print("No friend posts to show!")
                
        elif choice == "4":
            post_id = input("Enter Post ID: ")
            post = network.get_post(post_id)
            if post:
                if (network.vertices[post.author] in network.vertices[username].adjacency_map) or (post.author == username):
                    if username in post.likes:
                        if network.unlike_post(post_id, username):
                            print("Post Unliked!")
                    else:
                        if network.like_post(post_id, username):
                            print("Post Liked!")
                    display_post(post)
                else:
                    print("You are not a friend of the Post Author!")
            else:
                print("Post not found!")
                
        elif choice == "5":
            post_id = input("Enter Post ID: ")
            post = network.get_post(post_id)
            if post:
                if (network.vertices[post.author] in network.vertices[username].adjacency_map) or (post.author == username):
                    display_post(post)
                    comment = input("Enter your comment: ")
                    if network.comment_on_post(post_id, username, comment):
                        print("Comment Added!")
                        display_post(post)
                    else:
                        print("Failed to add comment!")
                else:
                    print("You are not a friend of the Post Author!")
            else:
                print("Post not Found!")
                
        elif choice == "6":
            break
        
        else:
            print("Invalid option!")

def main():
    while True:
        print("\n======== LinkUs ========")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        option = input("Choose an option >> ")
        
        if option == "1":
            name = input("Enter your name: ")
            while True:
                username = input("Enter a username: ")
                if not validate_username(username): # Checks if entered username is valid based on RegEx rules
                    print("Invalid username! Try again with only letters, numbers, underscore and period")
                    continue
                if trie.search(username): # Checks if such a username already exists (using Trie)
                    print("Username already exists! Please try again.")
                    continue
                trie.insert(username) # If no problems encountered, username is accepted and inserted in the Trie
                break
            hobbies = input("Enter hobbies (comma-separated): ").split(",")
            hobbies = [h.strip() for h in hobbies if h.strip()]
            description = input("Enter a personal description: ")
            network.add_person(name, username, hobbies, description)
            hobby_network.add_user_hobbies(username, hobbies)
            print(f"Account for {username.lower()} created successfully!")
        
        elif option == "2":
            username = get_username("Enter the Username: ")
            while True:
                print(f"\n==== Welcome, {username} ====")
                print("1. Get Friend Recommendations")
                print("2. Search Users")
                print("3. View Users by Hobby")
                print("4. Inbox")
                print("5. Send Message")
                print("6. View Messages")
                print("7. Posts")
                print("8. Logout")
                choice = input("Choose an option: ")
                
                if choice == "1":
                    print("\n==== Friend Recommendations ====")
                    recommendations = recommender.get_recommendations(username)
                    
                    if not recommendations:
                        print("No recommendations available at this time!")
                        print("Try adding more information to your profile or connecting with more people.")
                        continue
                        
                    print("\nHere are some people you might know:")
                    for i, (recommended_user, score) in enumerate(recommendations, 1):
                        person = network.vertices[recommended_user]
                        # Calculate common friends for display
                        common_friends = network.common_friends(username, recommended_user)
                        
                        # Format the score as a percentage
                        match_percentage = int(score * 100)
                        
                        print(f"\n{i}. {recommended_user}")
                        print(f"   Name: {person.name}")
                        print(f"   Hobbies: {', '.join(person.hobbies)}")
                        print(f"   Common Friends: {common_friends}")
                        print(f"   Match Score: {match_percentage}%")
                        
                    confirmation = input('\nDo you want to send any friend requests (yes/no)?: ')
                    if confirmation.lower() not in {'y','yes'}:
                        continue
                    while True:
                        try:
                            user_num = input("Enter the user number you want to connect with: ")
                            if user_num.isdigit() and 1 <= int(user_num) <= len(recommendations):
                                recommended_user = recommendations[int(user_num) - 1][0]
                                if network.send_friend_request(username, recommended_user):
                                    print(f"\nFriend request sent to {recommended_user}!")
                                else:
                                    print("\nCouldn't send friend request. They might have already received a request from you.")
                                break
                            else:
                                print("Invalid user number. Please try again!")
                        except ValueError:
                            print("Invalid input. Please enter a number!")
                    
                elif choice == "2":
                    search_username = get_username("Enter Username to Search: ", username)
                    if search_username != username:
                        person = network.vertices[search_username]
                        print(f"\n==== User Profile: {search_username} ====")
                        print(f"Name: {person.name}")
                        print(f"Hobbies: {', '.join(person.hobbies)}")
                        if person.description:
                            print(f"Description: {person.description}")
                        
                        # Show connection status
                        is_friend = person in network.vertices[username].adjacency_map
                        has_pending_request = search_username in network.vertices[username].inbox
                        received_request = username in person.inbox
                        
                        if is_friend:
                            print("\nStatus: Friend ✓")
                            common_friends_count = network.common_friends(username, search_username)
                            print(f"Common Friends: {common_friends_count}")
                        else:
                            print("\nStatus: Not Connected")
                            
                        while True:
                            print("\nOptions:")
                            if is_friend:
                                print("1. View Posts")
                                print("2. Send Message")
                                print("3. Back")
                            elif received_request:
                                print("1. Accept Friend Request")
                                print("2. Back")
                            elif has_pending_request:
                                print("1. Friend Request Pending")
                                print("2. Back")
                            else:
                                print("1. Send Friend Request")
                                print("2. Back")
                            
                            sub_choice = input("Choose an option: ")
                            
                            if is_friend:
                                if sub_choice == "1":
                                    posts = network.get_user_posts(search_username)
                                    if posts:
                                        print("\nUser Posts:")
                                        for pid, post in posts:
                                            print(f"\nPost ID: {pid}")
                                            print(post)
                                            print("Liked by:", ", ".join(post.likes) if post.likes else "No likes yet")
                                            if post.comments:
                                                print("\nComments:")
                                                for commenter, comment, timestamp in post.comments:
                                                    print(f"  {commenter} ({timestamp.strftime('%Y-%m-%d %H:%M')}): {comment}")
                                    else:
                                        print("No posts to show!")
                                elif sub_choice == "2":
                                    message = input("Enter your message: ")
                                    if network.send_message(username, search_username, message):
                                        print("Message sent successfully!")
                                    else:
                                        print("Failed to send message.")
                                elif sub_choice == "3":
                                    break
                            elif received_request:
                                if sub_choice == "1":
                                    if network.accept_friend_request(username, search_username):
                                        print(f"Yay! You are now friends with {search_username}!")
                                        break
                                    else:
                                        print("Failed to accept friend request.")
                                elif sub_choice == "2":
                                    break
                            elif has_pending_request:
                                if sub_choice in {"1", "2"}:
                                    break
                            else:
                                if sub_choice == "1":
                                    if network.send_friend_request(username, search_username):
                                        print("Friend request sent successfully!")
                                        break
                                    else:
                                        print("Failed to send friend request.")
                                elif sub_choice == "2":
                                    break
                            
                            if sub_choice not in {"1", "2", "3"}:
                                print("Invalid option! Please try again.")
                    else:
                        print("You can't search yourself :(")
                    
                elif choice == "3":
                    while True:
                        print("\n==== Hobby Management Menu ====")
                        print("1. List all hobbies with user counts")
                        print("2. Show most popular hobbies")
                        print("3. Find users with most hobbies")
                        print("4. View hobby trends")
                        print("5. View users for any hobby")
                        print("6. Back to Main Menu")

                        hobby_choice = input("Choose an option: ")

                        if hobby_choice == "1":
                            # List all hobbies with user counts
                            hobby_counts = hobby_network.get_hobby_counts()
                            print("\nHobbies and User Counts:")
                            for hobby, count in hobby_counts.items():
                                print(f"{hobby}: {count} user(s)")

                        elif hobby_choice == "2":
                            # Show top hobbies
                            top_hobbies = hobby_network.get_top_hobbies(limit=10)
                            print("\nTop 10 Most Popular Hobbies:")
                            for hobby, count in top_hobbies:
                                print(f"{hobby}: {count} user(s)")

                        elif hobby_choice == "3":
                            # Show users with most hobbies
                            users = hobby_network.get_users_with_most_hobbies(limit=10)
                            print("\nUsers with Most Hobbies:")
                            for username, count in users:
                                print(f"{username}: {count} hobbies")

                        elif hobby_choice == "4":
                            # Show hobby trends
                            trends = hobby_network.get_hobby_trends(days=30)
                            print("\nHobby Trends (Last 30 Days):")
                            for hobby, trend_data in trends.items():
                                if trend_data:
                                    latest = trend_data[-1]
                                    print(f"{hobby}: {latest[1]} users (as of {latest[0].strftime('%Y-%m-%d %H:%M')})")

                        elif hobby_choice == "5":
                            # View users for specific hobby
                            hobby = input("Enter hobby name: ")
                            users = hobby_network.get_users_by_hobby(hobby)
                            if users:
                                print(f"\nUsers interested in {hobby}:")
                                for user in users:
                                    print(user)
                            else:
                                print("No users found for this hobby.")

                        elif hobby_choice == "6":
                            break

                        else:
                            print("Invalid option! Please try again.")
                    
                elif choice == "4":
                    friend_requests = network.get_friend_requests(username)
                    if friend_requests:
                        print("Pending friend requests:")
                        for i, requester in enumerate(friend_requests, start=1):
                            print(f"{i}. {requester}")
                        selected = input("Enter number to accept request (or 0 to skip): ")
                        if selected.isdigit() and 1 <= int(selected) <= len(friend_requests):
                            requester = friend_requests[int(selected) - 1]
                            if network.accept_friend_request(username, requester):
                                print(f"Yay! You are now friends with {requester}!")
                            else:
                                print("Failed to Accept Friend Request.")
                    else:
                        print("No pending Friend Requests.")
                
                elif choice == "5":
                    to_user = get_username("Enter the Username of the recipient: ", username)
                    message = input("Enter your message: ")
                    if network.send_message(username, to_user, message):
                        print("Message sent successfully!")
                    else:
                        print("Failed to send message. Check if the user is your friend.")
                
                elif choice == "6":
                    messages = network.get_messages(username)
                    if messages:
                        print("\nYour Messages:")
                        for msg in messages:
                            print(msg)
                    else:
                        print("\nNo messages found.")

                elif choice=="7":
                    handle_post_menu(network, username)
                
                elif choice == "8":
                    print(f"\nLogging out {username}...")
                    break
                
                else:
                    print("Invalid option. Please try again!")
        
        elif option == "3":
            print("\nThanks for using LinkUs....")
            break
        
        else:
            print("Invalid option. Please try again!")

if __name__ == "__main__":
    main()
