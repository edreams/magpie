
def supported_resources():
    from ai21 import Completion, Dataset, CustomModel, Paraphrase, Tokenization, Summarize, Segmentation, Improvements, GEC

    return {
        'completion': Completion,
        'tokenization': Tokenization,
        'dataset': Dataset,
        'customModel': CustomModel,
        'paraphrase': Paraphrase,
        'summarization': Summarize,
        "segmentation": Segmentation,
        "improvements": Improvements,
        "gec": GEC
    }
