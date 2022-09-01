import tweepy

consumer_key = 'LlQY1SDjuUEZnfIZX3xK1KvZW'
consumer_secret = 'fqVJYoXJLX6JQZzaBPo7tbhLrz3BXQVS5Pb9ZfvzhiTGzjfq82'
access_token = '1564008155297845254-aC5IVAt7N7LIseREzz3ow9zox6eBjl'
access_token_secret = 'qybNdvWdtUCjzZNl7aq8D3M1G9RscVax5fOHYzVw9KYIa'

client = tweepy.Client(
	consumer_key=consumer_key,
	consumer_secret=consumer_secret,
	access_token=access_token,
	access_token_secret=access_token_secret
)

def publish_tweet(line_formula):
	client.create_tweet(text=line_formula)