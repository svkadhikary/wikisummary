import nltk
import re
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor


class Summarizer:
    def __init__(self):
        pass

    def initial_cleaing(self, body):
        body = re.sub(r'\[[0-9]*]', " ", body)
        body = re.sub(r'\s+', " ", body)

        sentences = nltk.sent_tokenize(body)
        sentences = [nltk.word_tokenize(sentence) for sentence in sentences]

        return body

    def summarize(self, body):
        body = self.initial_cleaing(body)

        auto_abstractor = AutoAbstractor()
        auto_abstractor.tokenizable_doc = SimpleTokenizer()
        auto_abstractor.delimiter_list = [".", "\n"]
        abstractable_doc = TopNRankAbstractor()

        result_dict = auto_abstractor.summarize(body, abstractable_doc)

        limit = 3
        i = 1
        summary = ""

        for sentence in result_dict['summarize_result']:
            summary += sentence
            if i >= limit:
                break
            i += 1

        return summary
