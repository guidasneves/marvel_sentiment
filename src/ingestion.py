import os
from requests import get
from requests.utils import default_headers
from hashlib import md5
from time import time
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

class MarvelIngestion():
    """
    
    """
    def __init__(
        self,
        public_key,
        private_key,
        url='http://gateway.marvel.com/v1/public/',
        limit=100,
    ):
        """
        
        """
        super(MarvelIngestion, self).__init__()

        self.public_key = public_key
        self.private_key = private_key
        
        self.url = url
        self.limit = 100

    def get_params(self, offset, format_=None):
        """
        
        """
        ts = str(time())
        hash_ = md5(
            (
                ts + self.private_key + self.public_key
            ).encode('utf-8')
        ).hexdigest()
        params = {
                'ts': ts,
                'apikey': self.public_key,
                'hash': hash_,
                'limit': self.limit,
                'offset': offset,
                'format': format_
            }

        return params
    
    def __call__(self, endpoint, offset=0, format_=None):
        """
        
        """
        examples = []
        
        endpoint = endpoint.lower().strip()
        key = 'name' if endpoint == 'characters' else 'title'
        params = self.get_params(offset=offset, format_=format_)
        headers = default_headers()
        response = get(self.url + endpoint, params=params, headers=headers).json()

        total = response['data']['total']
                
        for page in range(offset, total + 1, self.limit):
            results = response['data']['results']
            
            for i in range(len(results)):
                print(f'Processando o exemplo {page + i}', end='\r')
                description = results[i]['description']
                example = [
                        results[i]['id'],
                        results[i][key],
                        description
                    ]
                if example not in examples and description and len(description) > 4:
                    examples.append(example)
                    
            params = self.get_params(offset=page + self.limit, format_=format_)
            response = get(self.url + endpoint, params=params, headers=headers).json()
        print(page)

        features = ['id', 'title', 'description']
        df = pd.DataFrame(examples, columns=features)

        return df


if __name__ == '__main__':
    PUBLIC_KEY = str(os.environ['MARVEL_PUBLIC_KEY'])
    PRIVATE_KEY = str(os.environ['MARVEL_PRIVATE_KEY'])

    ingestion = MarvelIngestion(PUBLIC_KEY, PRIVATE_KEY)
    df = ingestion(endpoint='comics', format_='comic')
    print(df.shape, '\n', df.head())
