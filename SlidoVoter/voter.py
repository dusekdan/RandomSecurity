import requests
import json
import sys
import signal
from time import sleep
from pathlib import Path

apiVersion = "v0.5"
getEventUrlEndpoint = "https://api.sli.do/{apiversion}/events?code={eventcode}"
likeEndpoint = "https://app2.sli.do/api/v0.5/events/{eventid}/questions/{questionid}/like"
authEndpoint = "https://app2.sli.do/api/v0.5/events/{eventguid}/auth"
config = {}

silent = False # Set this to True to suppress the output.

# LOG MARKERS
INFO = "I"; WARNING = "W"; ERROR = "E"

def main(args):
    # Handle autoconf request
    if len(args) >= 3 and args[1] == "autoconf":
        config = autoconf(args[2])
        
        if config != False:
            log(INFO, "Config written:\n\t[DUMP] " + str(config)) 
            print("\nPlease run vote.py with question ID, number of votes and delay between them now. If you specify fourth parameter (any) dislike will be executed.")
        else:
            log(ERROR, "Error occurred when attempting autoconfiguration. Please set up config manually.")
    
    elif len(args) >= 2 and (args[1] == "-help" or args[1] == "--help" or args[1] == "-h" or args[1] == "help"):
        showHelp()
    
    elif len(args) >= 2 and args[1] != "autoconf": 
        # Check config existence
        if not isConfigPresent():
            log(ERROR, "Config does not exist. Either run this application with 'autoconf YOUREVENTCODE', or copy file 'config.example.json' to 'config.json' and manually set variable values there. Then you can run this script again.")
            exit(1)

        config = loadConfigValues()

        questionNumber, numberOfVotes, timeout, isDislike = extractVotingParameters(args)
        if questionNumber == False:
            log(ERROR, "Question number must be an integer number.")
            return False
        
        log(INFO, "" + str(numberOfVotes) + " vote(s) will be casted for question #" + str(questionNumber) + " with " + str(timeout) + "ms delay between each vote.")

        # Send vote(s) 
        s = requests.session()
        for i in range(numberOfVotes):
            vote(questionNumber, config["event_id"], config["event_guid"], isDislike, s)
            if timeout > 0:
                log(INFO, "Waiting for " + str(timeout) + " ms")
                sleep(timeout / 1000.0)
    else:
        showHelp()

def autoconf(eventCode):
    resolvedUrl = getEventUrlEndpoint.replace("{apiversion}", apiVersion).replace("{eventcode}", eventCode)
    
    try:
        eventUrlRequest = requests.get(resolvedUrl)
        log(INFO, "GET request to " + resolvedUrl + " was sent.")
        jsonData = json.loads(eventUrlRequest.text)[0]
        eventUrl = jsonData["url"]["app"]
        eventId = jsonData["event_id"]
        eventGuid = jsonData["uuid"]
        config = { 'event_url' : eventUrl, 'event_id' : eventId, 'event_guid' : eventGuid }

        with open('config.json', 'w') as fp:
            json.dump(config, fp)

        log(INFO, "Event url retrieved: " + eventUrl)
        return config
    except requests.exceptions.RequestException:
        log(ERROR, "Request to remote server failed.")
        log(ERROR, "Unable to fetch data from Sli.do endpoint. There are several possible causes:\n")
        print("\t > Provided event code for autoconfiguration does not exist or is no longer valid.\n")
        print("\t > Slido API version changed. See -help for information on how to update API version.\n")
        print("\t > [Some other issue related to connection between you and slido server.]\n")
        #print("\t > Slido hosts their API under versioned routes (e.g. /v0.4/, /v0.5/) and their version got upgraded. To fix this issue, try entering the room via their website (using your code) and inspecting requests sent by your browser. If you see a request to /api/vX.Y/events?code=YOURCODE, please open this script and set apiVersion variable to the value corresponding to vX.Y route name.")
        return False
    except (KeyError, ValueError):
        log(ERROR, "Response from Slido endpoint has changed. It will not be possible to recover from this error without updating a code.")
        return False
    except IndexError:
        log(ERROR, "Event code is probably incorrect.")
        return False

def log(marker, text):
    global silent
    if silent == False:
        print("[" + marker + "] " + text)

def retrieveToken(eventGuid, session):
    try:
        response = session.post(authEndpoint.replace("{eventguid}", eventGuid))
        token = json.loads(response.text)["access_token"]
        return token
    except requests.exceptions.RequestException:
        log(ERROR, "Error occurred while establishing connection to slido endpoint.")
        return False    


def vote(questionId, eventId, eventGuid, isDislike, session):
    token = retrieveToken(eventGuid, session)
    if (token != False):
        headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                'Accept' : 'application/json, text/plain, */*',
                'Accept-Language' : 'en-US,en;q=0.5',
                'Accept-Encoding' : 'gzip, deflate',
                'Content-Type' : 'application/json;charset=utf-8',
                'Authorization' : 'Bearer ' + token
        } 

        # Cast a vote by executing post request against corresponding slide endpoint (like)
        try:
            if isDislike:
                session.post(likeEndpoint.replace("{eventid}", str(eventId)).replace("{questionid}", str(questionId)), headers=headers, data="{\"score\":-1}")
            else:
                session.post(likeEndpoint.replace("{eventid}", str(eventId)).replace("{questionid}", str(questionId)), headers=headers)
            log(INFO, "Vote casted.")
        except requests.exceptions.RequestException:
            log(ERROR, "Error occurred while casting a vote.")
    else:
        log(ERROR, "Unable to cast a vote - the voting token could not be retrieved.")

def isConfigPresent():
    return Path('config.json').is_file()

def loadConfigValues():
    return json.load(open('config.json'))

def extractVotingParameters(args):
    # Try parsing an argument and if not possible (whatever the reason, return
    # default value).
    try:
        questionNumber = int(args[1])
    except ValueError:
        questionNumber = False

    try:
        numberOfVotes = int(args[2])
    except IndexError:
        log(INFO, "Number of votes not specified. Default value of 1 will be used.")
        numberOfVotes = 1
    except ValueError:
        log(WARNING, "Number of votes to be executed was expected to be a number, but not a number was supplied. Falling back to default: 1.")
        numberOfVotes = 1
    
    try:
        timeout = int(args[3])
    except IndexError:
        log(INFO, "Timeout was not specified. Default value of 0 will be used.")
        timeout = 0
    except ValueError:
        log(WARNING, "Timeout is expected to be a number, but not a number was supplied. Default value of 0 will be used.")
        timeout = 0

    try:
        isDislike = args[4]
        isDislike = True
    except IndexError:
        log(INFO, "Standard like")
        isDislike = False

    return (questionNumber, numberOfVotes, timeout, isDislike)


def showHelp():
    print("Sli.do Voter - 1.0")
    print("author:\tDaniel Dusek (@dusekdan)")
    print("reqs:\tpython3+, installed requests library (pip install requests)")
    print("usage:\tpython vote.py\tautoconf eventcode\n\t\t\tquestionId [number of votes (int)] [delay between votes in miliseconds]\n")
    print("Run vote.py script with autoconf option and event code first to create config ")
    print("file (config.json) for given event. After that proceed to open event in the ")
    print("browser and use Developer tools to inspect the request being sent to Slido")
    print("server when upvoting a question. It should point to 'like' endpoint, like this\n")
    print("\thttps://app2.sli.do/api/v0.5/events/YYYYY/questions/XXXXX/like")
    print("\t\t|=> XXXXX - a question number which you will pass to vote.py script\n")
    print("TROUBLESHOOTING\n")
    print("\tautoconf failed\n\t\tRefer to GIT-HUB-ADDRESS-HERE: Section on how to set up config.json manually.\n")
    print("\tslido api changed\n\t\tSlido uses versioned API and the version was updated. In such case, open vote.py")
    print("\tin editor of your choice and at the beginning of the code, update apiVersion variable value. To ")
    print("\tdetermine current slido API version, inspect requests being sent when entering their event via ")
    print("\tevent code text-box on their homepage.\n")

def signal_handler(signal, frame):
    print("[^C] CTRL+C pressed. Terminating the program.")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)