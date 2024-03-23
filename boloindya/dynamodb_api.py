import datetime

from django.conf import settings

from connection import dynamo_client

client = dynamo_client()

dynamo_type_map = {
    int: "N",
    bool: "BOOL",
    str: "S",
    float: "N"
}

def dict_to_dynamodb_dict(data):
    print "inside data", data
    _dict = {}

    for key, value in data.iteritems():
        _type = type(value)
        print "key, type", key, _type
        value_type = None, None
        if _type in (datetime.datetime, datetime.date):
            value_type, value = 'S', str(value)

        elif _type in (bytes, unicode):
            value_type, value = 'S', value.decode() 

        elif _type in (int, float):
            value_type, value = 'N', str(value)

        elif _type == dict:
            value_type, value = 'M', dict_to_dynamodb_dict(value)

        else:
            value_type = dynamo_type_map.get(_type)

        _dict[key] = {
            value_type: value
        }

    return _dict


def dynamodb_dict_to_dict(data):
    _data = {}
    for key, value in data.iteritems():
        main_value = value.values()[0]

        if type(main_value) == dict:
            main_value = dynamodb_dict_to_dict(main_value)

        _data[key] = main_value

    return _data


def dynamo_query_till_end(**params):
    last_evaluated_key = None
    items = []

    while True:
        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key

        response = client.query(**params)
        last_evaluated_key = response.get("LastEvaluatedKey")
        items += response.get("Items", [])

        if response.get("Count") == 0 or last_evaluated_key is None:
            break

    return items

def get_next_sequence(table_name):
    sequence_name = '%s_seq'%table_name
    counter_table_name = 'Counter_%s'%settings.DYNAMODB_ENV
    key = {
        'seq_name': {
            'S': sequence_name,
        },
    }
    try:
        response = client.update_item(
            Key=key,
            ReturnValues='ALL_NEW',
            TableName=counter_table_name,
            ExpressionAttributeValues={
                ':c': {
                    'N': '1',
                },
            },
            UpdateExpression='SET next_value = next_value + :c',
        )
        return int(response.get('Attributes').get('next_value').get('N'))
    except Exception as e:
        client.put_item(
            Item={
                'seq_name': {
                    'S': sequence_name
                },
                'next_value': {
                    'N': '1'
                }
            },
            ReturnConsumedCapacity='TOTAL',
            TableName=counter_table_name,
        )
        return 1


def create(table_name, data):
    item_data = dict_to_dynamodb_dict(data)
    item_data['id'] = {
        'N': str(get_next_sequence(table_name))
    }
    response = client.put_item(
        Item=item_data,
        ReturnConsumedCapacity='TOTAL',
        TableName=table_name,
    )


def query(table_name, expression_attribute_values, key_condition_expression):
    return map(dynamodb_dict_to_dict, dynamo_query_till_end(
        ExpressionAttributeValues=expression_attribute_values,
        KeyConditionExpression=key_condition_expression,
        TableName=table_name
    ))

