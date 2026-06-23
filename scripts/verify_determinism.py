import sys
import os
sys.path.insert(0, os.path.abspath('src'))

import json
from candidate_processor.models import Candidate
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.parser import CandidateParser

def main():
    parser = CandidateParser()
    cands = list(parser.stream('data/candidates_1000.jsonl'))

    print('Running serial...')
    serial_ext = CandidateFeatureExtractor()
    serial_recs = [serial_ext.extract(c) for c in cands]

    print('Running multiprocess...')
    multi_ext = CandidateFeatureExtractor()
    multi_recs = list(multi_ext.extract_stream_multiprocess((c for c in cands), chunk_size=100))

    print('Comparing...')
    identical = True
    for i, (s, m) in enumerate(zip(serial_recs, multi_recs)):
        if s.candidate_id != m.candidate_id:
            print(f'Order mismatch at {i}: {s.candidate_id} vs {m.candidate_id}')
            identical = False
        s_dict = s.to_row()
        m_dict = m.to_row()
        if s_dict != m_dict:
            print(f'Feature mismatch at {i} for {s.candidate_id}')
            identical = False

    if identical:
        print('SUCCESS: Both pipelines produce perfectly identical records in the exact same order.')
    else:
        print('FAILURE: Pipelines differ.')

if __name__ == '__main__':
    main()
