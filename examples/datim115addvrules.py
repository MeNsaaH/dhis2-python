import os
from dhis.config import Config
from dhis.server import Server
from dhis.types import Generic

#api=Server()
api=Server()
#api=Server(Config(config_url))
#api=Server(Config({..}))

#from dhis.config import Config; from dhis.server import Server; api=Server(Config('/src/hisp/home/secrets/datim221.json'))

def get_dataset(obj):
    if type(obj) is str:
        return api.get('dataSets/'+obj,return_type='object')
    else:
        return api.get('dataSets/'+obj.id,return_type='object')

def get_datasets(field,prefix):
    results=[]
    for ds in api.get('dataSets',return_type='collection'):
        val=ds.get(field)
        if type(val) is str and val.startswith(prefix):
            results.append(get_dataset(ds['id']))
    return results

def get_dataelement(obj):
    if type(obj) == str:
        id=obj
    else:
        id=obj.get('id')
    return api.get('dataElements/'+id,return_type='object')

def get_dataelement_byname(name):
    result=api.get('dataElements',
                   params={'filter': "name:eq:"+name,'fields': 'id'},
                   return_type='collection')
    if len(result) == 0:
        return None
    elif len(result) == 1:
        return get_dataelement(result[0]['id'])
    else:
        raise Exception('ambiguous name '+name)

def get_dataelements():
    elements=[]
    elementids=[]
    datasets=get_datasets('code','MER_TARGET')
    for ds in datasets:
        dselements=ds.dataElements
        for e in dselements:
            name=e.get('name')
            eid=e.get('id')
            if '(' in name and ')' in name:
                if eid not in elementids:
                    elementids.append(eid)
                    elements.append(get_dataelement(eid))
    return elements

def catcombo(obj):
    if type(obj) == str:
        id=obj
    else:
        id=obj.get('id')
    return api.get('categoryCombos/'+id,return_type='object')

def get_catcombo(elt):
    return get_catcombo(elt.get('categoryCombos'))

def catoptioncombo(obj):
    if type(obj) == str:
        id=obj
    else:
        id=obj.get('id')
    return api.get('categoryOptionCombos/'+id,return_type='object')

def vrule(obj):
    if type(obj) == str:
        id=obj
    else:
        id=obj.get('id')
    return api.get('validationRules/'+id,return_type='object')

def get_catoptioncombos(elt):
    return list(map(catoptioncombo,elt.get('categoryOptionCombos')))

def make_validation_rules(elt):
    name=elt.name
    left=name.index('(')
    right=name.index(')')
    body=name[left+1:right-1]
    args=body.split(',')
    rules=[]
    if len(args) > 2:
        numerator_name=name[0:left+1]+args[0]+","+args[1]+name[right:]
        print('numerator name='+numerator_name)
        numerator=get_dataelement_byname(numerator_name)
        if not numerator:
            print("Can't find data element numerator "+numerator_name+" for data element "+name+" ("+elt.id+")")
        else:
            rule=new_validation_rule(elt,numerator,args[2].strip().replace( '/', ' and ' ))
            rules.append(rule)
    return rules

def new_validation_rule(data_element,numerator,disaggregation):
    numerator_category=catcombo(numerator.categoryCombo)
    numerator_option_combos=get_catoptioncombos(numerator_category)
    left_expr="#{"+numerator.id+"."+numerator_option_combos[0].id
    data_category=catcombo(data_element.categoryCombo)
    data_option_combos=get_catoptioncombos(data_category)
    right_expr=""
    for option in data_option_combos:
        if len(right_expr)>0:
            right_expr=right_expr+" + "
        right_expr = right_expr+"#{"+data_element.id+"."+option.id+"}"
    left_expression={'description': numerator.shortName,
                     'missingValueStrategy': 'NEVER_SKIP',
                     'expression': left_expr}
    right_expression={'description': "Total of aggregations for "+data_element.shortName,
                     'missingValueStrategy': 'NEVER_SKIP',
                     'expression': right_expr}
    new_name=(data_element.name+" - vs. total")
    print('Making new validation rule '+new_name)
    return cons_validation_rule(
        {"name": new_name,
         "description":
         (numerator.shortName+" must equal or exceed the disaggregation by "+disaggregation+"."),
         "instruction":
         ("The "+numerator.shortName+" numerator must equal or exceed the disaggregation by "+disaggregation+"."),
         "ruletype": "VALIDATION",
         "importance": "MEDIUM",
         "periodType": "FinancialOct",
         "operator": "greater_than_or_equal_to",
         "rightSide": right_expression,
         "leftSide": left_expression})

def cons_validation_rule(template):
    return api.post('validationRules',jsondata=template,return_type='request')

def main():
    local_config=os.path.abspath("dhis2conf.json")
    if not os.path.isfile(local_config):
        print("Warning: The credentials file "+local_config+" doesn't seem to exist, so this might not work.")
    todo=get_dataelements()
    for elt in todo:
        make_validation_rules(elt)

if __name__ == "__main__":
    main()

