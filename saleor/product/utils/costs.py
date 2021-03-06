from prices import TaxedMoneyRange

from ...core.utils import ZERO_TAXED_MONEY


def get_product_costs_data(product):
    purchase_costs_range = TaxedMoneyRange(
        start=ZERO_TAXED_MONEY, stop=ZERO_TAXED_MONEY)
    gross_margin = (0, 0)

    if not product.variants.exists():
        return purchase_costs_range, gross_margin

    variants = product.variants.all()
    costs_data = get_cost_data_from_variants(variants)
    if costs_data.costs:
        purchase_costs_range = TaxedMoneyRange(
            min(costs_data.costs), max(costs_data.costs))
    if costs_data.margins:
        gross_margin = (costs_data.margins[0], costs_data.margins[-1])
    return purchase_costs_range, gross_margin


class CostsData:
    __slots__ = ('costs', 'margins')

    def __init__(self, costs, margins):
        self.costs = sorted(costs, key=lambda x: x.gross)
        self.margins = sorted(margins)


def get_cost_data_from_variants(variants):
    costs = []
    margins = []
    for variant in variants:
        costs_data = get_variant_costs_data(variant)
        costs += costs_data.costs
        margins += costs_data.margins
    return CostsData(costs, margins)


def get_variant_costs_data(variant):
    costs = []
    margins = []
    costs.append(get_cost_price(variant))
    margin = get_margin_for_variant(variant)
    if margin:
        margins.append(margin)
    return CostsData(costs, margins)


def get_cost_price(variant):
    if not variant.cost_price:
        return ZERO_TAXED_MONEY
    return variant.get_total()


def get_margin_for_variant(variant):
    variant_cost = variant.get_total()
    if variant_cost is None:
        return None
    price = variant.get_price_per_item()
    margin = price - variant_cost
    percent = round((margin.gross / price.gross) * 100, 0)
    return percent
