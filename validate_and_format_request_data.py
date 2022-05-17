import decimal
from collections import deque

class RequestDataValidationAndFormatting(object):
    def __init__(self, request_data):
        self.request_data = request_data
        self.missing_mandatory_data = []
        self.stack = deque()
        self._initialize_stack_with_request_data()
        
    def _initialize_stack_with_request_data(self):
        self._push_container_items_on_stack(self.request_data, '')
        
    def _is_missing_value(self, value):
        return value in [{}, [], '', None]

    def _add_address_to_missing_mandatory_data(self, address):
        self.missing_mandatory_data.append(address)
    
    def _is_container(self, value):
        return isinstance(value, (dict, list))
        
    def _is_string(self, value):
        return isinstance(value, str)
        
    def _is_decimal_number(self, value):
        return isinstance(value, (float, decimal.Decimal))
        
    def _is_top_level_container(self, container):
        return container is self.request_data
        
    def _get_child_address(self, key, container, address):
        child_address = f'{address}[{key}]'
        if self._is_top_level_container(container):
            child_address = key
        return child_address
        
    def _get_items_to_push_on_stack(self, container):
        items_to_push_on_stack = list()
        if isinstance(container, dict):
            items_to_push_on_stack = container.items()
        elif isinstance(container, list):
            items_to_push_on_stack = enumerate(container)
        return items_to_push_on_stack

    def _push_single_element_on_stack(self, key, value, container, address):
        self.stack.append((key, value, container, address))
        
    def _push_container_items_on_stack(self, container, address):
        items_to_push_on_stack = self._get_items_to_push_on_stack(container)
        for key, value in items_to_push_on_stack:
            child_address = self._get_child_address(key, container, address)
            self._push_single_element_on_stack(key, value, container, child_address)
            
    def _replace_unwanted_characters(self, key, value, container, address):
        container[key] = value.replace('&', 'and')
        if self._is_missing_value(container[key]):
            self._add_address_to_missing_mandatory_data(address)
        
    def _round_to_two_decimal_places(self, key, value, container, address):
        container[key] = round(float(value), 2)
        if self._is_missing_value(container[key]):
            self._add_address_to_missing_mandatory_data(address)
    
    def perform_tasks_and_get_missing_mandatory_data(self):
        while self.stack:
            key, value, container, address = self.stack.pop()
            if self._is_missing_value(value):
                self._add_address_to_missing_mandatory_data(address)
            elif self._is_container(value):
                self._push_container_items_on_stack(value, address)
            elif self._is_string(value):
                self._replace_unwanted_characters(key, value, container, address)
            elif self._is_decimal_number(value):
                self._round_to_two_decimal_places(key, value, container, address)
        return self.missing_mandatory_data


m1 = {
    'a': 'A',
    'b': 1.11,
    'c': [1.111111,22,33],
    'd': {
        'aa': 'AA',
        'bb': 'BB',
        'cc': 'CC',
        'dd': {
            'aaa': 'A & AA',
            'bbb': 'BBB',
            'ccc': 'CCC',
            'ddd': [
                {'aaaa':['AAAA', []]},
                {'aaaa':{}},
                {'aaaa':'AAAA'},
                {'aaaa':'AAAA'}
            ]
        }
    }
}

print(RequestDataValidationAndFormatting(m1).perform_tasks_and_get_missing_mandatory_data())