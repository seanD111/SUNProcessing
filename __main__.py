from . import argparse

from . import SUNProcessing


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory', help = '''Root directory of the SUN
    	database.''')

    args = vars(parser.parse_args())
    args = {k: v for k, v in args.items() if v}

    if 'directory' in args:
    	SUNProcessing.get_class_information(args['directory'])
    else:
    	print('Run SUNProcessing with -h to see possible arguments')	

    # parser.add_argument('-q', '--query', help='''Query the mesh and hpo database
    #     for all terms related to the inputted term''')
    # parser.add_argument('-l', '--levels', type = int, default = 1, 
    #     help='Levels of terms above the query term to expand') 
    # parser.add_argument('-f', '--fetch', action="store_true",
    #     help='Fetch HPO and MeSH terms and store them locally')    
    # parser.add_argument('-u', '--upload', action="store_true",
    #     help='Upload local HPO and MeSh terms to given mongo host')
    # parser.add_argument('-host', '--mongohost', 
    #     default= 'localhost:27017', help='''Specify the location where 
    #     mongodb server is being hosted''')



    # if 'fetch' in args:
    #     ExPhenosion.fetch_terms()
    # elif 'upload' in args:
    #     ExPhenosion.upload_terms(mongohost = args['mongohost'])
    # elif 'query' in args:
    #     ExPhenosion.query_database(args['query'], mongohost = args['mongohost'], 
    #         levels= args['levels'])
    # else:
    #     print('Run ExPhenosion with the -h argument to see possible arguments')