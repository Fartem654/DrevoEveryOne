from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render
from .models import Person, Marriage
import json

# Create your views here.

def get_family_graph_data():
    people = Person.objects.all().prefetch_related(
        'children_from_father',
        'children_from_mother',
        'marriages_as_husband',
        'marriages_as_wife'
    )

    nodes = []
    edges = []

    # УЗЛЫ: люди
    for person in people:
        nodes.append({
            "data": {
                "id": f"p{person.id}",
                "label": f"{person.first_name} {person.last_name}",
                "gender": person.gender,
                "alive": person.death is None,
            }
        })

    # РЕБРА: родители → дети
    for person in people:
        if person.father:
            edges.append({
                "data": {
                    "source": f"p{person.father.id}",
                    "target": f"p{person.id}",
                    "type": "parent-child",
                    "direction": "father"
                }
            })
        if person.mother:
            edges.append({
                "data": {
                    "source": f"p{person.mother.id}",
                    "target": f"p{person.id}",
                    "type": "parent-child",
                    "direction": "mother"
                }
            })

    # РЕБРА: браки
    marriages_seen = set()  # чтобы не дублировать рёбра
    for marriage in Marriage.objects.all():
        p1_id = f"p{marriage.husband.id}"
        p2_id = f"p{marriage.wife.id}"

        edge_key = tuple(sorted([p1_id, p2_id]))  # чтобы избежать дублей A-B и B-A

        if edge_key not in marriages_seen:
            edges.append({
                "data": {
                    "source": p1_id,
                    "target": p2_id,
                    "type": "spouse",
                    "married": not marriage.divorced,
                    "date": str(marriage.married_date) if marriage.married_date else None
                }
            })
            marriages_seen.add(edge_key)

    # Возвращаем структуру графа
    return {"nodes": nodes, "edges": edges}


def family_graph_json(request):
    data = get_family_graph_data()
    return JsonResponse(data)


def index(request):
    shef = 100
    return render(request, 'DApp/index.html', context={"shef": shef})
