#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

access_token = " 811672150000209920-BWfcDSP74HxA2Qo77OCkEdUcZQfKQZS"
access_token_secret = "QiLKmJPjMwbb8jO8GOvwkGNf2Kyvdm75ZGknuflnzIDPC"
consumer_key = " Q8Cv91TXQirAXCK8gstCm4IVU"
consumer_secret = " jdr3NnWbyY61fFsRGpiZTMm3JUnNrfog1gIZkT8baFCKOMuMfL"

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['python', 'javascript', 'ruby'])
