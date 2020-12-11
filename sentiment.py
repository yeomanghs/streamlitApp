
#import modules
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import pandas as pd
import pathlib
import re
import sys
from streamlit import cli

#current working dir
wd = str(pathlib.Path().absolute())

cutSentenceFile = wd + "\\Data\\CutSentence.xlsx"
df = pd.read_excel(cutSentenceFile)
cutSentenceDict = df.set_index('Original').to_dict()['Replacement']

def cutSentence(text):
    #cut sentence
    if re.search('|'.join(cutSentenceDict.keys()), text):
        matchList = re.findall('|'.join(cutSentenceDict.keys()), text)
        for match in matchList:
            text = re.sub(match, cutSentenceDict[match], text)     
    return text

#between -1 (most extreme negative) and +1 (most extreme positive)
def giveSentimentScore(text):
    analyzer = SentimentIntensityAnalyzer()
    #cut sentence
    text = cutSentence(text)
    sentimentscore = analyzer.polarity_scores(text)
    score = sentimentscore['compound']
    return score

def magnifyScore(text, overriding = False):
    splitPoint = 'Share price reaction:'
    firstText = text.split(splitPoint)[0]
    # secondText = re.sub('\-','minus ', re.sub('\+', 'plus ', text.split(splitPoint)[1]))
    #if no share price reaction in section of more details
    if len(text.split(splitPoint)) == 1:
        secondText = re.sub('\-','minus ', re.sub('\+', 'plus ', text.split(splitPoint)[0]))
    else:
        secondText = re.sub('\-','minus ', re.sub('\+', 'plus ', text.split(splitPoint)[1]))
    maxNum = 5
    magnifier = 3

    weightFirstText = 1/(magnifier + 1)
    weightSecondText = magnifier/(magnifier + 1)
    #use number in percent as weightage
    if re.search('-*(\d+(\.\d+)*)%', secondText):
        numberPercent = float(re.search('(\d+(\.\d+)*)%', secondText).group(1))

        #try to identify key phrase preceding numberPercent
        PositivePhraseList = ["rose", "rose by", "soared", "soared as much as"]
        NegativePhraseList = ["declined", "declined by", "slumped", "slumped by", "fell", "fell by"]
        #check if there is positive/negative phrase preceding numberPercent
        if re.search("(" + "|".join(PositivePhraseList + NegativePhraseList) + ")\s%s"%numberPercent, secondText):
            secondText = re.search("(" + "|".join(PositivePhraseList + NegativePhraseList) + ")\s%s"%numberPercent, secondText).group(1)
            keyPhrase = secondText
        else:
            keyPhrase = ''

        #if number is more than maxNum
        if numberPercent >= maxNum:
            #if overriding is selected
            if overriding == True:
                #print('Sentiment (second part text): %s'%self.giveSentimentScore(secondText))
                return giveSentimentScore(secondText)
            else:
                numberWeight = 1
                #if no keyPhrase identified
                if keyPhrase == "":
                    secondText = re.search('(.*?\d+(\.\d+)*%(\s\w+){0,2})', secondText).group(1)
                if giveSentimentScore(secondText) == 0:
                    return weightFirstText*giveSentimentScore(firstText)
                else:
                    return weightFirstText*giveSentimentScore(firstText) + weightSecondText*numberWeight*(giveSentimentScore(secondText)/abs(giveSentimentScore(secondText)))
        else:
            numberWeight = numberPercent/maxNum
            #print('Sentiment (second part text): %s'%self.giveSentimentScore(secondText))
            #print('Number of weight: %s'%numberWeight)
            return weightFirstText*giveSentimentScore(firstText) + weightSecondText*numberWeight*giveSentimentScore(secondText)
    else:
        numberWeight = 1
        #print('Sentiment (second part text): %s'%self.giveSentimentScore(secondText))
        #print('Number of weight: %s'%numberWeight)
        return weightFirstText*giveSentimentScore(firstText) + weightSecondText*numberWeight*giveSentimentScore(secondText)

#title
st.sidebar.title('Sentiment Score App')    
    
#start of app
textInput = st.text_input('Text Input for Sentiment Score')
st.write('Sentiment Score: ', giveSentimentScore(textInput))

# if __name__ == '__main__':

#     sys.argv = ["streamlit", "run", "sentiment.py"]
#     sys.exit(cli.main())
