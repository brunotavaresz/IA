#encoding: utf8

# YOUR NAME: Bruno Tavares Meixedo
# YOUR NUMBER: 113372

# COLLEAGUES WITH WHOM YOU DISCUSSED THIS ASSIGNMENT (names, numbers):
# - 113962
# - 113763
# - 112714

from collections import deque
from semantic_network import *
from constraintsearch import *
from bayes_net import *

class MySN(SemanticNetwork):

    def __init__(self):
        SemanticNetwork.__init__(self)

    def query(self, target_entity, relation_name):
        relevant_relations = [
            decl for decl in self.declarations if decl.relation.name == relation_name
        ]

        if not relevant_relations:
            return []  # se não houver relações para o nome de relação dado, retorna lista vazia
        
        # contagem de tipos de relações
        relation_types = {
            "AssocOne": 0, "AssocNum": 0, "AssocSome": 0, "Member": 0, "Subtype": 0
        }

        for decl in relevant_relations:
            relation_kind = type(decl.relation).__name__
            if relation_kind in relation_types:
                relation_types[relation_kind] += 1
        
        # tipo de relação predominante
        dominant_relation_type = max(relation_types, key=relation_types.get)

        filtered_relations = [
            decl for decl in relevant_relations if type(decl.relation).__name__ == dominant_relation_type
        ]

        # relações tipo
        if dominant_relation_type in {"Member", "Subtype"}:
            return list(set(
                decl.relation.entity2
                for decl in filtered_relations if decl.relation.entity1 == target_entity
            ))

        elif dominant_relation_type == "AssocOne":
            return self.process_assoc_one(filtered_relations, target_entity)

        elif dominant_relation_type == "AssocNum":
            return self.process_assoc_num(filtered_relations, target_entity)

        elif dominant_relation_type == "AssocSome":
            return self.process_assoc_some(filtered_relations, target_entity, relation_name)

        return []

    def process_assoc_one(self, relations, target_entity):
        # AssocOne
        entity_count = {}
        current_entity = target_entity

        while current_entity:
            for decl in relations:
                if decl.relation.entity1 == current_entity:
                    entity_count[decl.relation.entity2] = entity_count.get(decl.relation.entity2, 0) + 1
            current_entity = self.find_predecessor(current_entity)

        return [max(entity_count, key=entity_count.get)] if entity_count else []

    def process_assoc_num(self, relations, target_entity):
        # AssocNum
        values = []
        current_entity = target_entity

        while current_entity:
            for decl in relations:
                if decl.relation.entity1 == current_entity:
                    values.append(float(decl.relation.entity2))
            current_entity = self.find_predecessor(current_entity)

        return [sum(values) / len(values)] if values else []

    def process_assoc_some(self, relations, target_entity, relation_name):
        # AssocSome
        result_entities = set()
        local_relations = self.query_local(e1=target_entity, relname=relation_name)
        result_entities.update(d.relation.entity2 for d in local_relations if isinstance(d.relation, AssocSome))

        # Consultar predecessores
        predecessors = [
            d.relation.entity2 for d in self.query_local(e1=target_entity) if isinstance(d.relation, (Subtype, Member))
        ]

        for predecessor in predecessors:
            predecessor_values = self.query(predecessor, relation_name)
            result_entities.update(predecessor_values)

        return list(result_entities)

    def find_predecessor(self, entity):
        # Encontra o predecessor de uma entidade
        for decl in self.declarations:
            if isinstance(decl.relation, (Subtype, Member)) and decl.relation.entity1 == entity:
                return decl.relation.entity2
        return None
    
class MyBN(BayesNet):

    def __init__(self):
        BayesNet.__init__(self)

    def test_independence(self, v1, v2, conditioned_on):
        graph = []

        def collect_ancestors(variable, ancestors=None):
            if ancestors is None:
                ancestors = set()
            
            for dep in self.dependencies.get(variable, []):
                parents = set(dep[0]).union(set(dep[1]))
                for parent in parents:
                    if parent not in ancestors:
                        ancestors.add(parent)
                        collect_ancestors(parent, ancestors)
            return ancestors
        
        ancestors_set = {v1, v2}
        ancestors_set.update(conditioned_on)
        
        for var in ancestors_set.copy():
            ancestors_set.update(collect_ancestors(var, ancestors_set))
        
        # Construção das relações entre variáveis
        for ancestor in ancestors_set:
            for dep in self.dependencies.get(ancestor, []):
                parents = set(dep[0]).union(set(dep[1]))
                for parent in parents:
                    if (ancestor, parent) not in graph and (parent, ancestor) not in graph:
                        graph.append((ancestor, parent))
            parents_list = list(set(dep[0]).union(set(dep[1])))
            for i in range(len(parents_list)):
                for j in range(i + 1, len(parents_list)):
                    if (parents_list[i], parents_list[j]) not in graph and \
                       (parents_list[j], parents_list[i]) not in graph:
                        graph.append((parents_list[i], parents_list[j]))

        filtered_graph = {edge for edge in graph if not any(g in edge for g in conditioned_on)}

        # Função para realizar a busca em profundidade
        def search(start, target):
            visited = set()
            stack = [start]
            while stack:
                current = stack.pop(0)
                if current == target:
                    return True
                if current not in visited:
                    visited.add(current)
                    neighbors = set()
                    for (a, b) in filtered_graph:
                        if a == current:
                            neighbors.add(b)
                        elif b == current:
                            neighbors.add(a)
                    stack.extend(neighbors - visited)
            return False

        # As variáveis são independentes se NÃO houver caminho conectando-as
        independence_status = not search(v1, v2)

        return filtered_graph, independence_status

class MyCS(ConstraintSearch):

    def __init__(self, variable_domains, variable_constraints):
        super().__init__(variable_domains, variable_constraints)
        self.solutions_set = set()

    def search_all(self, variable_domains=None, max_solutions=None):
        self.solutions_set = set()
        self.calls = 0

        if variable_domains is None:
            variable_domains = self.domains

        stack = deque([variable_domains.copy()])

        while stack and (max_solutions is None or len(self.solutions_set) < max_solutions):
            current_domains = stack.pop()

            if any([lv == [] for lv in current_domains.values()]):
                continue

            if all([len(lv) == 1 for lv in current_domains.values()]):
                valid_solution = all(
                    self.constraints[var_a, var_b](var_a, current_domains[var_a][0], var_b, current_domains[var_b][0])
                    for (var_a, var_b) in self.constraints
                )

                if valid_solution:
                    solution = tuple(sorted((var, lv[0]) for (var, lv) in current_domains.items()))
                    self.solutions_set.add(solution)
                continue

            var_to_expand = self.select_variable(current_domains)

            if var_to_expand is not None and len(current_domains[var_to_expand]) > 1:
                values_to_explore = current_domains[var_to_expand]

                for val in values_to_explore:
                    new_domains = current_domains.copy()
                    new_domains[var_to_expand] = [val]
                    new_domains = self.propagate(new_domains, var_to_expand, val)
                    if new_domains is not None:
                        stack.append(new_domains)

        return [dict(solution) for solution in self.solutions_set]

    def select_variable(self, domains):
        return min(domains.keys(), key=lambda var: len(domains[var]) if len(domains[var]) > 1 else float('inf'))

    def propagate(self, domains, var, value):
        for var_b, domain in domains.items():
            if var_b == var:
                continue
            if (var_b, var) in self.constraints:
                constraint = self.constraints[var_b, var]
                new_domain = [val for val in domain if constraint(var_b, val, var, value)]
                if new_domain == []:
                    return None
                domains[var_b] = new_domain

        return domains

def handle_ho_constraint(domains, constraints, variables, constraint):
    combined_var = ''.join(variables)
    
    def check_constraint(values):
        return constraint(values)
    
    def generate_combinations(vars_left, current_values=None):
        if current_values is None:
            current_values = []
        
        if not vars_left:
            if check_constraint(tuple(current_values)):
                domains_combination.append(tuple(current_values))
            return
        
        current_var = vars_left[0]
        for value in domains[current_var]:
            generate_combinations(vars_left[1:], current_values + [value])
    
    domains_combination = []
    generate_combinations(variables)
    
    domains[combined_var] = domains_combination
    
    # restrições
    def create_binary_constraint(var, idx):
        def binary_constraint(v1, val1, v2, val2):
            # compara os valores de acordo com o índice
            return val2[idx] == val1 if v1 == var else val1[idx] == val2
        return binary_constraint
    
    for i, var in enumerate(variables):
        constraints[(var, combined_var)] = create_binary_constraint(var, i)
        constraints[(combined_var, var)] = create_binary_constraint(var, i)
    
    return domains, constraints
