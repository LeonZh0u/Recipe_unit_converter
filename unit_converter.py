import csv
import os
import re
from utils import *
from graph import *

def import_conversions(filename) -> list:
    """Import ingredient conversion table
    Returns:
        list: List of dicts (ingredient, cup, tablespoon, teaspoon)
    """

    with open(filename) as csvfile:
        conversion_table = list(csv.reader(csvfile, delimiter=","))

    header = conversion_table[0]
    conversion_table.pop(0)

    # Convert list of lists to list of dicts
    out_table = []
    for line in conversion_table:
        d = {
            header[0]: line[0],
            header[1]: string_to_float(line[1]),
            header[2]: string_to_float(line[2]),
            header[3]: string_to_float(line[3]),
        }
        out_table.append(d)

    return out_table

def create_graph(filename) -> DiGraph:
    
    node_cnt = 0;
    with open(filename) as csvfile:
        conversion_table = list(csv.reader(csvfile, delimiter=","))
    graph = DiGraph()
    for line in conversion_table:
        n1, unit1 = line[0].split(" ")
        n2, unit2 = line[1].split(" ")
        n1 = string_to_float(n1) if string_to_float(n1) else fraction_to_float(n1)
        n2 = string_to_float(n2) if string_to_float(n2) else fraction_to_float(n2)
        if graph.add_node(node_cnt, unit1):
            node_cnt+=1
        if graph.add_node(node_cnt, unit2):
            node_cnt+=1
        id1, id2 = graph.unit_to_id[unit1], graph.unit_to_id[unit2]
        
        graph.add_edge(id1, id2, n2/n1)
        graph.add_edge(id2, id1, n1/n2)
        
    return graph

class UnitConverter:

    OUNCE_TO_GRAM = 28.3495
    POUND_TO_GRAM = 453.592

    def __init__(self):
        database_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "gram-conversions.csv"
        )
        unit_graph_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "unit_to_unit.csv"
        )

        self._conversion_table = import_conversions(database_path)
        self.graph = create_graph(unit_graph_path)
        print(unit_graph_path, self.graph.v_size())

    def convert_recipe(self, recipe: str, multiplier=1.0) -> str:
        #Convert a multi-line recipe from volumetric units to mass units
        output = ""
        for line in recipe.split("\n"):
            try:
                output += self.convert_volume_to_mass(line, multiplier) + "\n"
            except Exception as e:
                print(f"Could not convert: '{line}''")
                print(repr(e))
                output += line + "\n"

        return output.strip()
    
    def convert_unit_to_unit(self, unit1: str, unit2: str, multiplier=1.0) -> float:
        visited =[False]*(self.graph.v_size()+1)
        rate = [-1]*(self.graph.v_size()+1)
        start, dest = self.graph.unit_to_id.get(unit1, None), self.graph.unit_to_id.get(unit2, None)
        if (not start or not dest):
            return -1;
        
        queue=[]
        queue.append(start)
        visited[start] = True
        rate[start]=1
        while queue:
            n = queue.pop(0)
            if n == dest:
                   return rate[n]*multiplier
            neighbours = self.graph.all_out_edges_of_node(n)
            for i in neighbours:
                if visited[i] == False:
                    rate[i] = rate[n]*neighbours[i]
                    queue.append(i)
                    visited[i] = True
        return -1
        
    def convert_volume_to_mass(self, line: str, multiplier=1.0) -> str:
        # Convert ingredient line from volume to mass.
        amount, unit, ingredient = self.extract_from_line(line.lower())

        amount = fraction_to_float(amount)

        if unit == "ounce":
            conversion = self.OUNCE_TO_GRAM
            unit = "g"
        elif unit == "pound":
            conversion = self.POUND_TO_GRAM
            unit = "g"
        else:
            conversion, unit = self.get_ingredient_conversion(ingredient, unit)

        amount_converted = amount * conversion * multiplier

        if amount_converted.is_integer():
            amount_converted = int(amount_converted)
        else:
            amount_converted = round(amount_converted, 1)

        # Incompatible ingredients won't have an associated unit
        if unit:
            unit_out = f" {unit} "
        else:
            unit_out = " "

        return f"{amount_converted}{unit_out}{ingredient}"

    def get_ingredient_conversion(self, ingredient: str, unit: str) -> float:
        # convert to gram if ingredient found in csv, else don't convert
        ingredient_found = False

        for conversion_line in self._conversion_table:
            if conversion_line["ingredient"] in ingredient:
                conversion = conversion_line[unit]
                ingredient_found = True
                break

        if not ingredient_found:
            conversion = 1
            unit_out = unit
        else:
            unit_out = "g"

        return conversion, unit_out

    @staticmethod
    def extract_from_line(line: str) -> tuple:
        # Extract components from ingredient line
        compatible_units = ["cup", "tablespoon", "teaspoon", "ounce", "pound"]
        regex_compatible = r"(.+?)(cup|tablespoon|teaspoon|ounce|pound)(?:s|)(.*)"
        regex_incompatible = r"(.+?)(?=[a-zA-z])(.*)"

        line = line.replace("tbsp", "tablespoon")
        line = line.replace("tsp", "teaspoon")
        line = line.replace("oz", "ounce")
        line = line.replace("lbs", "pound")
        line = line.replace("lb", "pound")

        if any(x in line for x in compatible_units):
            p = re.compile(regex_compatible)
            m = p.findall(line)

            amount = m[0][0].strip()
            unit = m[0][1].strip()
            ingredient = m[0][2].strip()

        else:
            p = re.compile(regex_incompatible)
            m = p.findall(line)

            amount = m[0][0].strip()
            unit = ""
            ingredient = m[0][1].strip()

        return amount, unit, ingredient