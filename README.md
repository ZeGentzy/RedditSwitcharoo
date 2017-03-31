Dependencies:
	A MySQL server running on "localhost" with a user "root" and a database called "REDDITSWITCHAROO" with a table called "foundposts" which has a colume called "commentID"
	Praw4
	mysqlclient
	[OPT] yappi

Directories:
|-- main.py 
|-- praw.ini
|-- psswd
\-- .gitignore

praw.ini:
Your going to need to define 2 bots:
	RedditSwitcharoo: Monitors all comments for switcharoos
	RedditSwitcharooTracer: Goes through comments
The bots do NOT have to be write capable
