# TextRank

## Description

This is an implementation of the TextRank algorithm for keyword extraction from documents. It adapts the PageRank algorithm to documents and was (originally published in 2004)[https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf].

## Usage

#### textrank.py

Gets the historical tweets of a list of users. If given a folder where tweet files of users exists, resumes from the last seen tweet. Suitable for running as a cron job in order to update the tweets at a regular time interval.

        python textrank.py folder

folder - folder with the documents to extract keywords

**Output**: a folder 'keywords-folder-textrank' with the keywords and their score, one per line, separated by a colon. This format can be used to generate word clouds using http://wordle.net/advanced

## Example 

Find the most central words from the US primary debate speeches.
	
	python textrank.py candidates

