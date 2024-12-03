import os

def parse_grammar_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    variables = lines[0].strip().split()
    start_symbol = lines[1].strip()
    rules = {}

    for line in lines[2:]:
        head, productions = line.strip().split("->")
        head = head.strip()
        productions = [prod.strip() for prod in productions.split("|")]
        if head not in rules:
            rules[head] = set()
        rules[head].update(productions)

    return variables, start_symbol, rules

def remove_empty_productions(variables, rules):
    nullable = set()

    for var in variables:
        if "h" in rules.get(var, []):
            nullable.add(var)

    changed = True
    while changed:
        changed = False
        for var, productions in rules.items():
            if var not in nullable and any(all(symbol in nullable for symbol in prod) for prod in productions):
                nullable.add(var)
                changed = True

    new_rules = {}
    for var, productions in rules.items():
        new_productions = set()
        for prod in productions:
            if prod == "h":
                continue
            symbols = list(prod)
            for i in range(1 << len(symbols)):
                new_prod = [symbols[j] for j in range(len(symbols)) if (i & (1 << j)) > 0]
                if new_prod:
                    new_productions.add("".join(new_prod))
        new_rules[var] = new_productions

    return new_rules

def remove_unit_productions(variables, rules):
    unit_pairs = set()

    for var in variables:
        for prod in rules.get(var, []):
            if prod in variables:
                unit_pairs.add((var, prod))

    changed = True
    while changed:
        changed = False
        new_pairs = set()
        for var1, var2 in unit_pairs:
            for prod in rules.get(var2, []):
                if prod in variables and (var1, prod) not in unit_pairs:
                    new_pairs.add((var1, prod))
                    changed = True
        unit_pairs.update(new_pairs)

    new_rules = {var: set() for var in variables}
    for var, productions in rules.items():
        for prod in productions:
            if prod not in variables:
                new_rules[var].add(prod)
    for var1, var2 in unit_pairs:
        new_rules[var1].update(rules.get(var2, []))

    return new_rules

def remove_useless_productions(variables, start_symbol, rules):
    generating = set()

    for var, productions in rules.items():
        if any(all(symbol not in variables for symbol in prod) for prod in productions):
            generating.add(var)

    changed = True
    while changed:
        changed = False
        for var, productions in rules.items():
            if var not in generating and any(all(symbol in generating or symbol not in variables for symbol in prod) for prod in productions):
                generating.add(var)
                changed = True

    reachable = set()
    reachable.add(start_symbol)
    stack = [start_symbol]

    while stack:
        var = stack.pop()
        for prod in rules.get(var, []):
            for symbol in prod:
                if symbol in variables and symbol not in reachable:
                    reachable.add(symbol)
                    stack.append(symbol)

    useful = generating & reachable
    new_rules = {var: set() for var in useful}

    for var in useful:
        for prod in rules.get(var, []):
            if all(symbol in useful or symbol not in variables for symbol in prod):
                new_rules[var].add(prod)

    return list(useful), new_rules

def simplify_grammar(file_path):
    variables, start_symbol, rules = parse_grammar_from_file(file_path)

    rules = remove_empty_productions(variables, rules)
    rules = remove_unit_productions(variables, rules)
    variables, rules = remove_useless_productions(variables, start_symbol, rules)

    return variables, start_symbol, rules

def format_output(variables, start_symbol, rules, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write(" ".join(variables) + "\\n")
        file.write(start_symbol + "\\n")
        for var, productions in rules.items():
            file.write(f"{var}->" + " | ".join(productions) + "\\n")

input_file = input("Digite o nome do arquivo de entrada (na pasta arquivos): ").strip()
input_path = os.path.join("arquivos", input_file)

if not os.path.exists(input_path):
    print(f"O arquivo '{input_path}' não foi encontrado.")
else:
    output_file = f"{os.path.splitext(input_file)[0]}_saida.txt"
    output_path = os.path.join("arquivos", output_file)
    
    variables, start_symbol, rules = simplify_grammar(input_path)
    format_output(variables, start_symbol, rules, output_path)
    
    print(f"Gramática simplificada salva em: {output_path}")
