#!python3

import json
import re
import subprocess
from typing import Any, List, Dict

import jinja2
import xxhash


def get_inventory() -> Dict[str, Any]:
  cmd = subprocess.run(["cue", "export", "inventory.cue"], capture_output=True, check=True)
  data = cmd.stdout.decode("utf-8")
  return json.loads(data)


def parse_nacl_rule(rule: str) -> Dict[str, str]:
  rule1 = re.sub(r"\s+", " ", rule)
  rule2 = rule1.split(" ")

  rule3 = {rule2[idx]: rule2[idx + 1] for idx in range(0, len(rule2), 2)}
  # TODO split port to source_port dest_port
  # TODO what about nuber of the ACL

  rule3["id"] = xxhash.xxh32(rule1).hexdigest()
  return rule3


def parse_nacl_rules(rules: List[str]) -> List[Dict[str, str]]:
  return [parse_nacl_rule(rule) for rule in rules]


def render_template(inventory: Dict[str, Any]) -> str:
  env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("./")
  )

  template = env.get_template("template.jinja2")
  return template.render(inventory)


def main():
  inventory = get_inventory()

  for nacl in inventory["nacl"]:
    rules = inventory["nacl"][nacl]

    ingress = parse_nacl_rules(rules["ingress"])
    egress = parse_nacl_rules(rules["egress"])

    inventory["nacl"][nacl]["ingress"] = ingress
    inventory["nacl"][nacl]["egress"] = egress

  # print(json.dumps(inventory))
  print(render_template(inventory))


main()
