from __future__ import with_statement

import praw
import threading
import time 
import regex

from collections import deque

import MySQLdb

#import yappi
#yappi.start()

file = open("/home/gentz/projects-python/RedditSwitcharoo/psswd", "r")
psswd = file.read()
file.close()

db = MySQLdb.connect(host="localhost",          # your host, usually localhost
                     user="root",               # your username
                     passwd=psswd,              # your password
                     db="REDDITSWITCHAROO")     # name of the data base
curDB = db.cursor()
dbLock = threading.Lock()

redditGrab = praw.Reddit('RedditSwitcharooTracer', user_agent='linux:RedditSwitcharoo:V0.1 PROTOTYPE GRABBING PAST (by /u/zegentz)', api_request_delay=1)

toHandle = deque([])
toHandleLock = threading.Lock()

active = 0
activeLock = threading.Lock()

commentIdRegex1 = regex.compile(r'[a-z0-9]{7}[\/\\][\?]')
commentIdRegex2 = regex.compile(r'[a-z0-9]{7}[\?]')
commentIdRegex3 = regex.compile(r'[a-z0-9]{7}[\/\\]\Z')
commentIdRegex4 = regex.compile(r'[a-z0-9]{7}\Z')
# Srsly Standardize your links reddit

def GetCommentId (linkToComment):
    commentId = "N/A"
    try:
        commentId = commentIdRegex1.search(linkToComment).group(0)[:-2]
    except (AttributeError):
        try:
            commentId = commentIdRegex2.search(linkToComment).group(0)[:-1]
        except (AttributeError):
            try:
                commentId = commentIdRegex3.search(linkToComment).group(0)[:-1]
            except (AttributeError):
                try:
                    commentId = commentIdRegex4.search(linkToComment).group(0)
                except (AttributeError):
                    print("[AttributeError] Are you sure this is a link: " + linkToComment)
    return commentId;

grabUrl = regex.compile(r'[hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\/\\]?[\?]?.*[\)]')

def HandleSwitch(name):  
    while True: 
        comment = "N/A"
        with toHandleLock:
            if toHandle:
                comment = toHandle.popleft()
        
        if comment != "N/A": 
            with activeLock:
                global active
                active += 1
                print ("HAN" + name + "-----MOVED ACTIVE UP TO: " + str(active))
            print("HAN" + name + "-----Started on: " + comment.fullname)
                                
            HandleSwitchINT(name, comment, redditGrab)
                
            print("HAN" + name + "-----Finished on: " + comment.fullname)
            
            with activeLock:
                active -= 1
                print ("HAN" + name + "-----MOVED ACTIVE DOWN TO: " + str(active))
    return

def HandleSwitchINT(name, comment, reddit):  
    if comment.fullname == "t1_removed":
        print (name + ": Got Removed.")
        return
    
    with dbLock: 
        curDB.execute('SELECT `id` FROM `foundposts` WHERE (`commentID`) = \'' + comment.fullname + '\';')   
        ret = curDB.fetchall()
        if ret != ():
            print ("INTHAN" + name + "----------" + comment.fullname + " Taken")
            return
    
        try:
            curDB.execute('INSERT INTO `foundposts` (`commentID`) VALUES (\'' + comment.fullname + '\');')   
            db.commit()
            print ("INTHAN" + name + "----------" + comment.fullname + " Claimed")
        except:
            db.rollback();
            return
    print (name + "------------COMMENT BODY ST------------\n\n" + comment.body + "\n\n------------COMMENT BODY EN------------")
    
    if comment.body == "[removed]":
        DetectSwitch(comment, True, True)
        return
    
    url = ""
    try:
        url = grabUrl.search(comment.body).group(0)[:-1]
        print (name + "-- FOUND URL " + url + " --")
    except:
        with dbLock:
            try:
                curDB.execute('DELETE FROM `foundposts` WHERE (`commentID`) = \'' + comment.fullname + '\';')   
                db.commit()
            except:
                db.rollback();
                return
        if comment.is_root == False:
            print (name + " " + comment.fullname + " has it somewhere")
            DetectSwitch(comment, True, True) # its somewhere up north or south... I hope
        else:
            print (name + " " + comment.fullname + " has it somewhere bellow")
            DetectSwitch(comment, False, True) # its somewhere up north or south... I hope
        
        return;
        
    commentId = GetCommentId(grabUrl.search(comment.body).group(0)[:-1])
    if commentId == "N/A":
        return    
        
    nComment = reddit.comment(id=commentId)
    
    print (name + " Par: " + nComment.fullname)
    
    with activeLock:
        lActive = active
            
    time.sleep (1 * lActive) # 1 sec delay per thread.
    
    HandleSwitchINT(name, nComment, reddit)
    return

# How does it work you ask?
# Not even god knows
#
# All I see is brakets
# I'm sure I'm doing it wrong
detectSwitchRegex1 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT]?[hH]?[eE]?[\[]?[ ][\[]?[oO][lL][dD\']?[\[]?[ ]?[\[]?[rR][eE][dD][dD][iI][tT].*[oO][oO].*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex2 = regex.compile(r'[\[]?[tT][hH][eE][\[]?[ ][\[]?[oO][lL][dD\']?[\[]?[ ]?[\[]?[rR][eE][dD][dD][iI][tT].*[oO][oO].*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex3 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT][hH][eE][\[]?[ ][\[]?[rR][eE][dD][dD][iI][tT].*[oO][oO].*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')

# Sometimes thier is a good
detectSwitchRegex4 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT]?[hH]?[eE]?[\[]?[ ][\[]?[gG][oO][oO][dD][\[]?[ ]?[\[]?[oO][lL][dD\']?[\[]?[ ][\[]?[rR][eE][dD][dD][iI][tT].*[oO][oO].*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex5 = regex.compile(r'[\[]?[tT][hH][eE][\[]?[ ][\[]?[gG][oO][oO][dD][\[]?[ ][\[]?[oO][lL][dD\']?[\[]?[ ]?[\[]?[rR][eE][dD][dD][iI][tT].*[oO][oO].*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex6 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT][hH][eE][\[]?[ ][\[]?[gG][oO][oO][dD][\[]?[ ][\[]?[rR][eE][dD][dD][iI][tT].*[oO][oO].*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')

# Sometimes reddit is not there
detectSwitchRegex7 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT]?[hH]?[eE]?[\[]?[ ][\[]?[oO][lL][dD\']?.*[aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?.*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex8 = regex.compile(r'[\[]?[tT][hH][eE][\[]?[ ][\[]?[oO][lL][dD\']?.*[aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?.*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex9 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT][hH][eE].*[aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?.*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex10 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT]?[hH]?[eE]?[\[]?[ ][\[]?[gG][aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?[dD][\[]?[ ]?[\[]?[oO][lL][dD\']?.*[aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?.*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex11 = regex.compile(r'[\[]?[tT][hH][eE][\[]?[ ][\[]?[gG][aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?[dD][\[]?[ ][\[]?[oO][lL][dD\']?.*[aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?.*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')
detectSwitchRegex12 = regex.compile(r'[\[]?[aA][hH][hH]?[,]?[\[]?[ ][\[]?[tT][hH][eE][\[]?[ ][\[]?[gG][aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?[dD].*[aA]?[\-]?[rR][\-]?[oO][oO][ ]?[!]?.*[\]][ ]?[\(][hH][tT][tT][pP][sS]?[\:][\/\\][\/\\].*[\.][rR][eE][dD][dD][iI][tT][\.][cC][oO][mM][\/\\][rR][\/\\].*[\/\\][cC][oO][mM][mM][eE][nN][tT][sS][\/\\].*[\/\\].*[\/\\].*[\%]?[0-9]?[0-9]?[\%]?[\/\\]?[\?]?.*[\)].*')

# And Old is sometimes not there
# Sometimes thier multilined
# Sometimes it just doesnt work
# goddamit reddit... make a standard
# I'm not going to cover the million and one extra variations

def RegexForSwitch(comment):
    try:
        detectSwitchRegex1.search(comment).group(0)
    except (AttributeError):
        try:
            detectSwitchRegex2.search(comment).group(0)
        except (AttributeError):
            try:
                detectSwitchRegex3.search(comment).group(0)
            except (AttributeError):
                try:
                    detectSwitchRegex4.search(comment).group(0)
                except (AttributeError):
                    try:
                        detectSwitchRegex5.search(comment).group(0)
                    except (AttributeError):
                        try:
                            detectSwitchRegex6.search(comment).group(0)
                        except (AttributeError):
                            try:
                                detectSwitchRegex7.search(comment).group(0)
                            except (AttributeError):
                                try:
                                    detectSwitchRegex8.search(comment).group(0)
                                except (AttributeError):
                                    try:
                                        detectSwitchRegex9.search(comment).group(0)
                                    except (AttributeError):
                                        try:
                                            detectSwitchRegex10.search(comment).group(0)
                                        except (AttributeError):
                                            try:
                                                detectSwitchRegex11.search(comment.body).group(0)
                                            except (AttributeError):
                                                try:
                                                    detectSwitchRegex12.search(comment.body).group(0)
                                                except (AttributeError):
                                                    return False
    return True;

def DetectSwitchChildren(comments):
    for comment in comments.list():
        DetectSwitch(comment, False, False)

def DetectSwitch(comment, checkParents, checkChildren):
    print ("----------------------------------------------------------------CONFIRMING " + comment.fullname)
    if RegexForSwitch(comment.body) == True:
        print ("----------------------------------------------------------------CONFIRMED " + comment.fullname)
        with toHandleLock:
            toHandle.append(comment)
    else:
        print("----------------------------------------------------------------NON--CONFIRMED " + comment.fullname)
        if checkParents == True:
            if comment.is_root == False:
                # Some people randomly link to random comments under it...
                # Oh how slow this will be
                print("----------------------------------------------------------------GOING TO PARENTS " + comment.fullname)
                t = threading.Thread(name="DetectSwitchPar" + comment.parent().fullname, target=DetectSwitch, args = (comment.parent(), True, False,))
                t.daemon = True
                t.start()

        if checkChildren == True:
                # Some people randomly deleteing thier crap
                # Oh how slowwer this will be
                comment.refresh();
                ncoms = comment.replies
                ncoms.replace_more(limit=0)
                
                print("----------------------------------------------------------------GOING TO CHILDREN " + comment.fullname)
                t = threading.Thread(name="DetectSwitchParChildrenOf" + comment.fullname, target=DetectSwitchChildren, args = (ncoms,))
                t.daemon = True
                t.start()
    return

def StreamSubreddit(subredditName, assumeValid, audible):
    reddit = praw.Reddit('RedditSwitcharoo', user_agent='linux:RedditSwitcharoo:V0.1 PROTOTYPE Monitoring:' + subredditName + ' (STREAM MODE) (by /u/zegentz)', api_request_delay=1.017)
    subreddit = reddit.subreddit(subredditName)
    
    for comment in subreddit.stream.comments():
        if comment.fullname == "t1_removed":
            print (" --- Got Removed. --- ")
            continue
        if audible:
            print ("----------------------------------------------------------------FOUND (STR) " + comment.fullname)
        if assumeValid:
            if audible:
                print ("----------------------------------------------------------------ASSUMING VALID " + comment.fullname)
            with toHandleLock:
                toHandle.append(comment)
        else:
            DetectSwitch(comment, False, False)

def WatchSubreddit(subredditName, assumeValid, audible, rate):
    reddit = praw.Reddit('RedditSwitcharoo', user_agent='linux:RedditSwitcharoo:V0.1 PROTOTYPE Monitoring:' + subredditName + ' (WATCH MODE) (by /u/zegentz)', api_request_delay=1.017)
    subreddit = reddit.subreddit(subredditName)

    while True:
        for submission in subreddit.new(limit=100):
            commentId = GetCommentId(submission.url)

            comment = reddit.comment(id=commentId)
            
            if comment.fullname == "t1_removed":
                print ("Got Removed.")
                continue

            if audible:
                print ("----------------------------------------------------------------FOUND " + comment.fullname)
            if assumeValid:
                if audible:
                    print ("----------------------------------------------------------------ASSUMING VALID " + comment.fullname)
                with toHandleLock:
                    toHandle.append(comment)
            else:
                DetectSwitch(comment, True, True)
                
        time.sleep(rate) # 24 hours

t1 = threading.Thread(name="WatchSwitcharoo", target=WatchSubreddit, args = ("switcharoo",True, True, 60 * 60 * 24,))
t1.daemon = True
t1.start()

t2 = threading.Thread(name="SwitcharooTracer1", target=HandleSwitch, args = ("1",))
t2.daemon = True
t2.start()

t3 = threading.Thread(name="SwitcharooTracer2", target=HandleSwitch, args = ("2",))
t3.daemon = True
t3.start()

t4 = threading.Thread(name="SwitcharooTracer3", target=HandleSwitch, args = ("3",))
t4.daemon = True
t4.start()

t5 = threading.Thread(name="SwitcharooTracer4", target=HandleSwitch, args = ("4",))
t5.daemon = True
t5.start()

t6 = threading.Thread(name="SwitcharooTracer5", target=HandleSwitch, args = ("5",))
t6.daemon = True
t6.start()

t7 = threading.Thread(name="WatchSwitcharoo", target=WatchSubreddit, args = ("ProjectSwitcharoo",True, True, 60 * 2,))
t7.daemon = True
t7.start()

redditOther = praw.Reddit('RedditSwitcharoo', user_agent='linux:RedditSwitcharoo:V0.1 PROTOTYPE OTHER (by /u/zegentz)', api_request_delay=1.017)
# Other Lines
with toHandleLock:
    toHandle.append(redditOther.comment(id="dfn3bju"))

StreamSubreddit("All", False, False)

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()
t7.join()

db.close()
print ("----PROFILER RESAULTS----")
#yappi.get_func_stats().print_all() 
#yappi.get_thread_stats().print_all()