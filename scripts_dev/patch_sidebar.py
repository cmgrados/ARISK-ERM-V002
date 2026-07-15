import re

file_path = r'c:\Users\USER\Desktop\A.RISK ERM C1\templates\base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We want to find the liquidity_risk li and remove everything until the end of risk_appetite li.
# We will use regex to replace this section.
pattern = re.compile(r'<li class="nav-item has-treeview \{% if request\.resolver_match\.app_name == \'liquidity_risk\'.*?ESTRATEGIA Y APETITO.*?</ul>\s*</li>', re.DOTALL)

new_menu = """<li class="nav-header" style="color: #ffffff; opacity:0.6;">NUEVOS MÓDULOS</li>
          <li class="nav-item">
            <a href="#" class="nav-link">
              <i class="nav-icon fas fa-bullseye text-success"></i>
              <p>Metas</p>
            </a>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link">
              <i class="nav-icon fas fa-search-dollar text-warning"></i>
              <p>Evaluación de Créditos</p>
            </a>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link">
              <i class="nav-icon fas fa-star text-info"></i>
              <p>Scoring</p>
            </a>
          </li>"""

new_content = pattern.sub(new_menu, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Patch applied successfully.")
