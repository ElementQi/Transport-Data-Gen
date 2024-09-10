# this code is referenced from https://aistudio.baidu.com/projectdetail/4388971?channelType=0&channel=0

import pandas as pd
from config import Config
import json
from tqdm import tqdm
import re
import argparse

class Pre(object):
    relations = {}
    labels = {}
    keys = []
    
    def __init__(self, output_file, data_modes, combine=False):
        self.cf = Config()
        self.air_travel = {} if combine else set()  # Use a dict if combine=True, otherwise use a set
        self.output_file = output_file
        self.data_modes = data_modes
        self.combine = combine
    
    def _detail2dk(self, detail, islist=False):
        if not islist:
            detail = detail.strip().replace(" ","").replace("'",'"')
            detail = json.loads(detail)
        dk = [str(i) for i in detail]
        dk = ','.join(dk)
        return dk

    def _contents(self):
        contents = pd.read_excel(self.cf.dataPath+'/sections.xlsx')
        for i in range(len(contents)):
            dk = self._detail2dk(contents.loc[i]['detail'])
            key = contents.loc[i]['content-key']+'-'+dk
            self.keys.append(key)
            self.relations[key] = contents.loc[i]['text']

    def _is_meaningful(self, context):
        """ Filter out meaningless content based on specific criteria """
        # Check if the context contains mostly symbols, empty, or placeholder text
        if len(context) <= 2 or re.match(r'^[\W\d_]+$', context):  # Filters very short and symbol-based content
            return False
        if '$$' in context:  # Filter out placeholder patterns
            return False
        return True

    def _data(self, mode):
        f = open(self.cf.dataPath + '/' + mode + '.txt', encoding='utf-8')
        lines = f.readlines()
        total_lines = len(lines)
        for line in tqdm(lines, total=total_lines, desc=f'Processing {mode} data'):
            data = line.strip().split('\t')
            data = json.loads(data[0])
            question = data['question']
            if question is None or question != question:
                continue

            for item in data['answer']:
                dk = self._detail2dk(item['detail'], True)
                key = item['content-key'] + '-' + dk
                if key in self.relations:
                    context = self.relations[key]
                    if self._is_meaningful(context):  # Check if the context is meaningful
                        if self.combine:
                            # Combine contexts for the same question
                            if question in self.air_travel:
                                if context not in self.air_travel[question]:
                                    self.air_travel[question] += " " + context
                            else:
                                self.air_travel[question] = context
                        else:
                            # Just add unique (question, context) pairs if not combining
                            self.air_travel.add((question, context))
        f.close()

    def run(self):
        self._contents()
        
        # Process datasets based on provided modes
        for mode in self.data_modes:
            self._data(mode)
        
        # Write the combined or uncombined dataset to the output file
        with open(self.output_file, 'w', encoding='utf-8') as myF:
            if self.combine:
                for question, context in self.air_travel.items():
                    re = {'question': question, 'context': context}
                    myF.write(json.dumps(re, ensure_ascii=False) + '\n')
            else:
                for question, context in self.air_travel:
                    re = {'question': question, 'context': context}
                    myF.write(json.dumps(re, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    # Set up argparse to allow command line inputs
    parser = argparse.ArgumentParser(description="Process datasets and combine them.")
    parser.add_argument('--output_file', type=str, default='mine/air_travel.txt', help='The name of the output file.')
    parser.add_argument('--data_modes', nargs='+', default=['train', 'valid'], help='List of dataset modes to process (e.g., train valid).')
    parser.add_argument('--combine', action='store_true', help='Flag to combine contexts for the same question.')

    args = parser.parse_args()

    # Initialize the Pre object with command line arguments and run the process
    pre = Pre(output_file=args.output_file, data_modes=args.data_modes, combine=args.combine)
    pre.run()
