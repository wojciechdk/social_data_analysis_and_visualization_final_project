# %%
import requests
import json


# %%


def get_table_metadata(table_code):
    output_format_metadata = 'JSON'
    language = 'en'

    url = (fr'https://api.statbank.dk/v1/tableinfo/'
           fr'{table_code}?'
           fr'lang={language}'
           fr'&format={output_format_metadata}')

    response_meta_data = requests.get(url.encode('utf-8'))
    meta_data = json.loads(response_meta_data.content)

    return meta_data


def get_table_columns(table_code):
    meta_data = get_table_metadata(table_code)
    columns = [
        {'id': column_data['id'],
         'name': column_data['text'].lower(),
         'categories': [{'id': category['id'],
                         'name': category['text'].lower()}
                        for category in column_data['values']]}
        for column_data in meta_data['variables']
    ]

    return columns


def get_table(table_code, path_output_file, categories: dict):
    # The output language (not for columns)
    language = 'en'

    # Get the columns of the table
    table_columns = get_table_columns(table_code)

    if categories == 'all':
        categories = {column['name']: ['*'] for column in table_columns}

    # Mark all the
    for column in table_columns:
        if column['name'] not in categories.keys():
            categories[column['name']] = [column['categories'][0]['name']]

    # Create a string for extraction of columns
    columns_str = ''
    for column in table_columns:
        columns_str += fr"&{column['id']}(Head)="
        for idx, category_name in enumerate(categories[column['name']]):
            if category_name == '*':
                category_id = '*'
            else:
                category_id = [cat['id'] for cat in column['categories']
                               if cat['name'] == category_name][0]

            if idx == 0:
                columns_str += fr"{category_id}"
            else:
                columns_str += fr'%2C{category_id}'

    output_format_table = 'BULK'

    # BULK
    url = (fr'https://api.statbank.dk/v1/data/'
           fr'{table_code}/'
           fr'{output_format_table}'
           fr'?'
           fr'lang={language}'
           fr'&valuePresentation=Value'
           fr'&delimiter=Tab'
           fr'{columns_str}')

    response = requests.get(url.encode('utf-8'))

    # Put true column names in the header
    new_header = '\t'.join([column['name'].capitalize()
                            for column in table_columns])

    new_table = (
            new_header.encode('utf-8')
            + '\r\n'.encode('utf-8')
            + response.content.partition('\r\n'.encode('utf-8'))[2]
    )

    # Save to file
    with open(path_output_file, 'wb') as output_file:
        output_file.write(new_table)


# %%
table_code = 'FOLK1A'
table_metadata = get_table_metadata(table_code)
table_columns = get_table_columns(table_code)
get_table(table_code,
          'data.csv',
          {'region': ['copenhagen'],
           'age': ['20 years'],
           'sex': ['men', 'women'],
           'marital status': ['*']})

# %%

# CSV
# url = (fr'https://api.statbank.dk/v1/data/'
#        fr'{table_code}/'
#        fr'{output_format_table}'
#        fr'?'
#        fr'lang={language}'
#        fr'&valuePresentation=Value'
#        fr'&timeOrder=Descending'
#        fr'&delimiter=Tab'
#        fr'&allowCodeOverrideInColumnNames=true'
#        fr'{columns_str}')
