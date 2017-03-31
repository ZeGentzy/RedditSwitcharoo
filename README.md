# RedditSwitcharoo
## Dependencies:
	* A MySQL server running on "localhost" with a user "root" and a database called "REDDITSWITCHAROO" with a table called "foundposts" which has a colume called "commentID"
	* aw4
	* sqlclient
	* [OPT] yappi

## Directories:
1. |-- main.py 
2. |-- praw.ini
3. |-- psswd
4. \-- .gitignore

### praw.ini:
Your going to need to define 2 bots:
	* RedditSwitcharoo: Monitors all comments for switcharoos
	* RedditSwitcharooTracer: Goes through comments
The bots do NOT have to be write capable
