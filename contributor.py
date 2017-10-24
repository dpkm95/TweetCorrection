import json, shutil, os, sys

class TweetCorrection():
    def __init__(self):
        self.config = json.loads(open('config.json').read())
        self.tweets = open(self.config['DATA_FILE_NAME']).read().split('\n')

    def display_rules(self):
        print('\nPLEASE READ THE BELOW RULES CAREFULLY AND APPLY AS NEEDED:')
        for rule in self.config['RULES']:
            print('* '+rule)
        print('\nStarting Tweet Correction...\n')


    def prompt_usn_input(self):
        try:
            self.usn = raw_input('Please enter your USN: ')
            self.output_dir = self.usn+'_output'
            assert(self.usn != '')
        except Exception:
            self.prompt_usn_input()

    def prompt_split_input(self):
        try:
            self.split_index = int(raw_input('Please enter split assigned to you: '))
            assert(self.split_index != '')
        except:
            self.prompt_split_input()

    def prompt_start_from_input(self):
        print('Tweet index exceeded your split bounds, ')
        try:
            self.split_start_index = int(raw_input('Please enter correct index to start from: '))
            assert(self.split_start_index < self.split_end_index)
        except:
            self.prompt_start_from_input()

    def prompt_tweet(self, tweet, count):
        print('\n\nTweet ' + str(count) + ': \"' + tweet + '\"')
        print

    def prompt_tweet_omission(self):
        omit = raw_input('Should the tweet be removed? (no) : ')
        return False if (omit in ['','no']) else True

    def prompt_sentiment_input(self):
        try:
            sentiment = raw_input('Please assign sentiment to tweet? (0 -negative, 1 -neutral, 2 -positive) : ')
            assert (sentiment in ['0', '1', '2'])
            return sentiment
        except:
            self.prompt_sentiment_input()

    def prompt_if_correction_needed(self):
        correction = raw_input('Does the tweet need correction? (yes) : ')
        return True if (correction in ['','yes']) else False

    def prompt_correction_input(self):
        correction = raw_input('Please enter the complete corrected tweet : ')
        return correction

    def prompt_before_save(self):
        save = raw_input('\nDo you want to save? (yes) : ')
        return True if (save in ['','yes']) else False

    def process_tweet(self, tweet, count):
        packet = {}
        self.prompt_tweet(tweet, count)

        omitted = self.prompt_tweet_omission()

        if not omitted:
            sentiment = self.prompt_sentiment_input()

            if self.prompt_if_correction_needed():
                correction_needed = True
                correction = self.prompt_correction_input()
            else:
                correction_needed = False

            if not self.prompt_before_save():
                self.process_tweet(tweet, count)
            else:
                if correction_needed:
                    packet['corrected_original_tweet_sentiment_tuple'] = (tweet, sentiment)
                    packet['corrected_changed_tweet_sentiment_tuple'] = (correction, sentiment)
                    self.save_output(packet)
                else:
                    packet['unchanged_tweet_sentiment_tuple'] = (tweet, sentiment)
                    self.save_output(packet)
        else:
            if not self.prompt_before_save():
                self.process_tweet(tweet, count)
            else:
                packet['omitted_tweet'] = tweet
                self.save_output(packet)

    def create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        for file in ['omitted_tweets.txt', 'unchanged_tweets.txt', 'corrected_original.txt', 'corrected_changed.txt']:
            open(os.path.join(self.output_dir, file), 'w').close()

    def save_output(self, packet):
        if 'omitted_tweet' in packet:
            with open(self.output_dir+'/omitted_tweets.txt','a') as f:
                f.write(packet['omitted_tweet']+'\n')
        else:
            if 'unchanged_tweet_sentiment_tuple' in packet:
                with open(self.output_dir+'/unchanged_tweets.txt','a') as f:
                    f.write(', '.join(packet['unchanged_tweet_sentiment_tuple'])+'\n')
            else:
                with open(self.output_dir+'/corrected_original.txt','w') as f:
                    f.write(', '.join(packet['corrected_original_tweet_sentiment_tuple'])+'\n')

                with open(self.output_dir+'/corrected_changed.txt','w') as f:
                    f.write(', '.join(packet['corrected_changed_tweet_sentiment_tuple'])+'\n')

    def zip_output(self):
        shutil.make_archive(self.output_dir, 'zip', self.output_dir)
        print('\nThank you for your contribution. Your work is saved into '+self.output_dir+'.zip')

    def setup(self):
        self.prompt_usn_input()
        self.prompt_split_input()
        self.display_rules()

        self.split_size = len(self.tweets) / int(self.config['NUMBER_OF_PARTICIPANTS'])
        self.split_end_index = len(self.tweets) if (self.split_size == self.split_index) \
            else (self.split_index) * self.split_size

    def run(self):
        self.setup()

        if len(sys.argv)==3 and sys.argv[1] == '--start-from':
            try:
                self.split_start_index = int(sys.argv[2])
                assert self.split_start_index < self.split_end_index
            except Exception:
                self.prompt_start_from_input()
        else:
            self.create_output_dir()
            self.split_start_index = (self.split_index-1) * self.split_size

        for tweet_index in range(self.split_start_index, self.split_end_index):
            tweet = self.tweets[tweet_index]
            self.process_tweet(tweet, tweet_index)
        else:
                self.zip_output()


app = TweetCorrection()
app.run()
