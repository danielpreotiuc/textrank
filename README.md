# TextRank

## Description
   
This is an implementation of the TextRank algorithm for keyword extraction from documents. It adapts the PageRank algorithm to documents and was [originally published in this article](https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf).

Intuitively, it builds a graph of words which are linked by the number of times they appear in the same context (here, same sentence). Then, it finds the words that most central in this graph, i.e. appear in context with as many other words from separate parts of the graph. The further refine, it performes part-of-speech tagging on all the debates and took into account only nouns as these are known to be most distinctive for summarization purposes. Then, a chunker identifies names like ‘Wall Street’ or ‘New York’ and collocations such as ‘ballistic missile’ or ‘coal miner’. Finally, it outputs lemmatized words in order to merge words with the same lemma such as ‘republican’ - ‘republicans’.

For the script to run, you need to [install NLTK](http://www.nltk.org/).

## Usage

#### textrank.py

        python textrank.py folder

folder - folder with the documents to extract keywords

**Output**: a folder 'keywords-folder-textrank' with the keywords and their score, one per line, separated by a colon. This format can be used to generate word clouds using [Wordle](http://wordle.net/advanced)

## Examples

Find the most central words from the US primary debate speeches.
	
	python textrank.py candidates

<center>
Bernie Sanders' primary Debate Speeches keywords generated using Wordle:
![Sanders' keywords](http://www.sas.upenn.edu/~danielpr/sanders-trsentw.png)
</center>
