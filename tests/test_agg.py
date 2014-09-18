from mock import Mock, patch

from elasticmagic import agg, Params, Term
from elasticmagic.expression import Fields

from .base import BaseTestCase


class AggregationTest(BaseTestCase):
    def test_aggs(self):
        f = Fields()

        a = agg.Avg(f.price)
        self.assert_expression(
            a,
            {
                "avg": {"field": "price"}
            }
        )
        a.process_results({
            'value': 75.3
        })
        self.assertAlmostEqual(a.value, 75.3)

        a = agg.Stats(f.grade)
        self.assert_expression(
            a,
            {
                "stats": {"field": "grade"}
            }
        )
        a.process_results(
            {
                "count": 6,
                "min": 60,
                "max": 98,
                "avg": 78.5,
                "sum": 471
            }
        )
        self.assertEqual(a.count, 6)
        self.assertEqual(a.min, 60)
        self.assertEqual(a.max, 98)
        self.assertAlmostEqual(a.avg, 78.5)
        self.assertEqual(a.sum, 471)

        a = agg.ExtendedStats(f.grade)
        self.assert_expression(
            a,
            {
                "extended_stats": {"field": "grade"}
            }
        )
        a.process_results(
            {
                "count": 6,
                "min": 72,
                "max": 117.6,
                "avg": 94.2,
                "sum": 565.2,
                "sum_of_squares": 54551.51999999999,
                "variance": 218.2799999999976,
                "std_deviation": 14.774302013969987
            }
        )
        self.assertEqual(a.count, 6)
        self.assertEqual(a.min, 72)
        self.assertAlmostEqual(a.max, 117.6)
        self.assertAlmostEqual(a.avg, 94.2)
        self.assertAlmostEqual(a.sum, 565.2)
        self.assertAlmostEqual(a.sum_of_squares, 54551.51999999999)
        self.assertAlmostEqual(a.variance, 218.2799999999976)
        self.assertAlmostEqual(a.std_deviation, 14.774302013969987)

        a = agg.Percentiles(f.load_time, percents=[95, 99, 99.9])
        self.assert_expression(
            a,
            {
                "percentiles": {
                    "field": "load_time",
                    "percents": [95, 99, 99.9]
                }
            }
        )
        a.process_results(
            {
                "values": {
                    "95.0": 60,
                    "99.0": 150,
                    "99.9": 2,
                }
            }
        )
        self.assertEqual(
            a.values,
            {'95.0': 60, '99.0': 150, '99.9': 2},
        )

        a = agg.PercentileRanks(f.load_time, values=[15, 30])
        self.assert_expression(
            a,
            {
                "percentile_ranks": {
                    "field": "load_time",
                    "values": [15, 30]
                }
            }
        )
        a.process_results(
            {
                "values": {
                    "15": 92,
                    "30": 100,
                }
            }
        )
        self.assertEqual(
            a.values,
            {'15': 92, '30': 100},
        )

        a = agg.Global()
        self.assert_expression(a, {"global": {}})

        a = agg.Filter(f.company == 1)
        self.assert_expression(a, {"filter": {"term": {"company": 1}}})

        a = agg.Terms(f.status)
        self.assert_expression(
            a,
            {
                "terms": {"field": "status"}
            }
        )
        a.process_results(
            {
                'buckets': [
                    {'doc_count': 7353499, 'key': 0},
                    {'doc_count': 2267139, 'key': 1},
                    {'doc_count': 1036951, 'key': 4},
                    {'doc_count': 438384, 'key': 2},
                    {'doc_count': 9594, 'key': 3},
                    {'doc_count': 46, 'key': 5}
                ]
            }
        )
        self.assertEqual(len(a.buckets), 6)
        self.assertEqual(a.buckets[0].key, 0)
        self.assertEqual(a.buckets[0].doc_count, 7353499)
        self.assertEqual(a.buckets[1].key, 1)
        self.assertEqual(a.buckets[1].doc_count, 2267139)
        self.assertEqual(a.buckets[2].key, 4)
        self.assertEqual(a.buckets[2].doc_count, 1036951)
        self.assertEqual(a.buckets[3].key, 2)
        self.assertEqual(a.buckets[3].doc_count, 438384)
        self.assertEqual(a.buckets[4].key, 3)
        self.assertEqual(a.buckets[4].doc_count, 9594)
        self.assertEqual(a.buckets[5].key, 5)
        self.assertEqual(a.buckets[5].doc_count, 46)

        a = agg.SignificantTerms(f.crime_type)
        self.assert_expression(
            a,
            {
                "significant_terms": {"field": "crime_type"}
            }
        )
        a.process_results(
            {
                "doc_count": 47347,
                "buckets" : [
                    {
                        "key": "Bicycle theft",
                        "doc_count": 3640,
                        "score": 0.371,
                        "bg_count": 66799,
                    },
                    {
                        "key": "Mobile phone theft",
                        "doc_count": 27617,
                        "score": 0.0599,
                        "bg_count": 53182,
                    }
                ]
            }
        )
        self.assertEqual(len(a.buckets), 2)
        self.assertEqual(a.buckets[0].key, 'Bicycle theft')
        self.assertEqual(a.buckets[0].doc_count, 3640)
        self.assertAlmostEqual(a.buckets[0].score, 0.371)
        self.assertEqual(a.buckets[0].bg_count, 66799)
        self.assertEqual(a.buckets[1].key, 'Mobile phone theft')
        self.assertEqual(a.buckets[1].doc_count, 27617)
        self.assertAlmostEqual(a.buckets[1].score, 0.0599)
        self.assertEqual(a.buckets[1].bg_count, 53182)

        a = agg.Filters([Term(f.body, 'error'), Term(f.body, 'warning')])
        self.assert_expression(
            a,
            {
                "filters": {
                    "filters": [
                        {"term": {"body": "error"}},
                        {"term": {"body": "warning"}}
                    ]
                }
            }
        )
        a.process_results(
            {
                "buckets": [
                    {
                        "doc_count" : 34
                    },
                    {
                        "doc_count" : 439
                    },
                ]
            }
        )
        self.assertEqual(len(a.buckets), 2)
        self.assertIs(a.buckets[0].key, None)
        self.assertEqual(a.buckets[0].doc_count, 34)
        self.assertIs(a.buckets[1].key, None)
        self.assertEqual(a.buckets[1].doc_count, 439)

        a = agg.Filters(Params(errors=Term(f.body, 'error'), warnings=Term(f.body, 'warning')))
        self.assert_expression(
            a,
            {
                "filters": {
                    "filters": {
                        "errors": {"term": {"body": "error"}},
                        "warnings": {"term": {"body": "warning"}}
                    }
                }
            }
        )
        a.process_results(
            {
                "buckets": {
                    "errors": {
                        "doc_count" : 34
                    },
                    "warnings": {
                        "doc_count" : 439
                    },
                }
            }
        )
        self.assertEqual(len(a.buckets), 2)
        self.assertIs(a.buckets[0].key, 'errors')
        self.assertEqual(a.buckets[0].doc_count, 34)
        self.assertIs(a.buckets[1].key, 'warnings')
        self.assertEqual(a.buckets[1].doc_count, 439)

        a = agg.Nested(f.resellers, aggs={'min_price': agg.Min(f.resellers.price)})
        self.assert_expression(
            a,
            {
                "nested": {"path": "resellers"},
                "aggregations": {
                    "min_price": {"min": {"field": "resellers.price"}}
                }
            }
        )
        a.process_results(
            {
                "min_price": {
                    "value" : 350
                }
            }
        )
        self.assertEqual(a.get_aggregation('min_price').value, 350)
        
        # complex aggregation with sub aggregations
        a = agg.Global(
            aggs={
                'selling_type': agg.Terms(
                    f.selling_type,
                    aggs={
                        'price_avg': agg.Avg(f.price),
                        'price_min': agg.Min(f.price),
                        'price_max': agg.Max(f.price),
                        'price_hist': agg.Histogram(f.price, interval=50),
                    }
                ),
                'price_avg': agg.Avg(f.price),
            }
        )
        self.assert_expression(
            a,
            {
                "global": {},
                "aggregations": {
                    "selling_type": {
                        "terms": {"field": "selling_type"},
                        "aggregations": {
                            "price_avg": {"avg": {"field": "price"}},
                            "price_min": {"min": {"field": "price"}},
                            "price_max": {"max": {"field": "price"}},
                            "price_hist": {"histogram": {"field": "price", "interval": 50}},
                        }
                    },
                    "price_avg": {"avg": {"field": "price"}}
                }
            }
        )
        a.process_results(
            {
                'doc_count': 100,
                'selling_type': {
                    'buckets': [
                        {
                            'key': 'retail',
                            'doc_count': 70,
                            'price_avg': {'value': 60.5},
                            'price_min': {'value': 1.1},
                            'price_max': {'value': 83.4},
                            'price_hist': {
                                'buckets': [
                                    {'key': 50, 'doc_count': 60},
                                    {'key': 100, 'doc_count': 7},
                                    {'key': 150, 'doc_count': 3},
                                ]
                            },
                        },
                        {
                            'key': 'wholesale',
                            'doc_count': 30,
                            'price_avg': {'value': 47.9},
                            'price_min': {'value': 20.1},
                            'price_max': {'value': 64.8},
                            'price_hist': {
                                'buckets': [
                                    {'key': 0, 'doc_count': 17},
                                    {'key': 50, 'doc_count': 5},
                                    {'key': 100, 'doc_count': 6},
                                    {'key': 150, 'doc_count': 2},
                                ]
                            },
                        },
                    ],
                },
                'price_avg': {'value': 56.3},
            }
        )
        self.assertEqual(a.doc_count, 100)
        type_agg = a.get_aggregation('selling_type')
        self.assertEqual(len(type_agg.buckets), 2)
        self.assertEqual(type_agg.buckets[0].key, 'retail')
        self.assertEqual(type_agg.buckets[0].doc_count, 70)
        self.assertAlmostEqual(type_agg.buckets[0].get_aggregation('price_avg').value, 60.5)
        self.assertAlmostEqual(type_agg.buckets[0].get_aggregation('price_min').value, 1.1)
        self.assertAlmostEqual(type_agg.buckets[0].get_aggregation('price_max').value, 83.4)
        price_hist_agg = type_agg.buckets[0].get_aggregation('price_hist')
        self.assertEqual(price_hist_agg.buckets[0].key, 50)
        self.assertEqual(price_hist_agg.buckets[0].doc_count, 60)
        self.assertEqual(price_hist_agg.buckets[1].key, 100)
        self.assertEqual(price_hist_agg.buckets[1].doc_count, 7)
        self.assertEqual(price_hist_agg.buckets[2].key, 150)
        self.assertEqual(price_hist_agg.buckets[2].doc_count, 3)
        self.assertEqual(len(price_hist_agg.buckets), 3)
        self.assertEqual(type_agg.buckets[1].key, 'wholesale')
        self.assertEqual(type_agg.buckets[1].doc_count, 30)
        self.assertAlmostEqual(type_agg.buckets[1].get_aggregation('price_avg').value, 47.9)
        self.assertAlmostEqual(type_agg.buckets[1].get_aggregation('price_min').value, 20.1)
        self.assertAlmostEqual(type_agg.buckets[1].get_aggregation('price_max').value, 64.8)
        price_hist_agg = type_agg.buckets[1].get_aggregation('price_hist')
        self.assertEqual(len(price_hist_agg.buckets), 4)
        self.assertEqual(price_hist_agg.buckets[0].key, 0)
        self.assertEqual(price_hist_agg.buckets[0].doc_count, 17)
        self.assertEqual(price_hist_agg.buckets[1].key, 50)
        self.assertEqual(price_hist_agg.buckets[1].doc_count, 5)
        self.assertEqual(price_hist_agg.buckets[2].key, 100)
        self.assertEqual(price_hist_agg.buckets[2].doc_count, 6)
        self.assertEqual(price_hist_agg.buckets[3].key, 150)
        self.assertEqual(price_hist_agg.buckets[3].doc_count, 2)
        self.assertEqual(a.get_aggregation('price_avg').value, 56.3)

    def test_instance_mapper(self):
        class _Gender(object):
            def __init__(self, key, title):
                self.key = key
                self.title = title

        Male = _Gender('m', 'Male')
        Female = _Gender('f', 'Female')
        GENDERS = {g.key: g for g in [Male, Female]}

        f = Fields()

        gender_mapper = Mock(return_value=GENDERS)
        a = agg.Terms(f.gender, instance_mapper=gender_mapper)
        a.process_results(
            {
                "buckets": [
                    {
                        "key": "m",
                        "doc_count": 10
                    },
                    {
                        "key": "f",
                        "doc_count": 10
                    },
                ]
            }
        )
        self.assertEqual(len(a.buckets), 2)
        self.assertEqual(a.buckets[0].instance.title, 'Male')
        self.assertEqual(a.buckets[1].instance.title, 'Female')
        self.assertEqual(gender_mapper.call_count, 1)

        gender_mapper = Mock(return_value=GENDERS)
        a = agg.Global(
            aggs={
                'all_genders': agg.Terms(f.gender, instance_mapper=gender_mapper),
                'all_salary': agg.Range(
                    f.month_salary,
                    ranges=[
                        {'to': 1000},
                        {'from': 1000, 'to': 2000},
                        {'from': 2000, 'to': 3000},
                        {'from': 3000},
                    ],
                    aggs={
                        'gender': agg.Terms(f.gender, instance_mapper=gender_mapper)
                    }
                )
            }
        )
        a.process_results(
            {
                "doc_count": 1819,
                "all_genders": {
                    "buckets": [
                        {
                            "key": "m",
                            "doc_count": 1212
                        },
                        {
                            "key": "f",
                            "doc_count": 607
                        }
                    ]
                },
                "all_salary": {
                    "buckets": [
                        {
                            "to": 1000,
                            "doc_count": 183,
                            "gender": {
                                "buckets": [
                                    {
                                        "key": "f",
                                        "doc_count": 101
                                    },
                                    {
                                        "key": "m",
                                        "doc_count": 82
                                    }
                                ]
                            }
                        },
                        {
                            "from": 1000,
                            "to": 2000,
                            "doc_count": 456,
                            "gender": {
                                "buckets": [
                                    {
                                        "key": "f",
                                        "doc_count": 231
                                    },
                                    {
                                        "key": "m",
                                        "doc_count": 225
                                    }
                                ]
                            }
                        },
                        {
                            "from": 2000,
                            "to": 3000,
                            "doc_count": 1158,
                            "gender": {
                                "buckets": [
                                    {
                                        "key": "m",
                                        "doc_count": 894
                                    },
                                    {
                                        "key": "f",
                                        "doc_count": 264
                                    }
                                ]
                            }
                        },
                        {
                            "from": 3000,
                            "doc_count": 22,
                            "gender": {
                                "buckets": [
                                    {
                                        "key": "m",
                                        "doc_count": 11
                                    },
                                    {
                                        "key": "f",
                                        "doc_count": 11
                                    }
                                ]
                            }
                        },
                    ]
                }
            }
        )
        self.assertEqual(a.doc_count, 1819)
        all_genders_agg = a.get_aggregation('all_genders')
        self.assertEqual(len(all_genders_agg.buckets), 2)
        self.assertEqual(all_genders_agg.buckets[0].key, 'm')
        self.assertEqual(all_genders_agg.buckets[0].doc_count, 1212)
        self.assertEqual(all_genders_agg.buckets[0].instance.title, 'Male')
        self.assertEqual(all_genders_agg.buckets[1].key, 'f')
        self.assertEqual(all_genders_agg.buckets[1].doc_count, 607)
        self.assertEqual(all_genders_agg.buckets[1].instance.title, 'Female')
        all_salary_agg = a.get_aggregation('all_salary')
        self.assertEqual(len(all_salary_agg.buckets), 4)
        self.assertIs(all_salary_agg.buckets[0].from_, None)
        self.assertEqual(all_salary_agg.buckets[0].to, 1000)
        self.assertEqual(all_salary_agg.buckets[0].doc_count, 183)
        gender_agg = all_salary_agg.buckets[0].get_aggregation('gender')
        self.assertEqual(len(gender_agg.buckets), 2)
        self.assertEqual(gender_agg.buckets[0].key, 'f')
        self.assertEqual(gender_agg.buckets[0].doc_count, 101)
        self.assertEqual(gender_agg.buckets[0].instance.title, 'Female')
        self.assertEqual(gender_agg.buckets[1].key, 'm')
        self.assertEqual(gender_agg.buckets[1].doc_count, 82)
        self.assertEqual(gender_agg.buckets[1].instance.title, 'Male')
        self.assertEqual(all_salary_agg.buckets[1].from_, 1000)
        self.assertEqual(all_salary_agg.buckets[1].to, 2000)
        self.assertEqual(all_salary_agg.buckets[1].doc_count, 456)
        gender_agg = all_salary_agg.buckets[1].get_aggregation('gender')
        self.assertEqual(len(gender_agg.buckets), 2)
        self.assertEqual(gender_agg.buckets[0].key, 'f')
        self.assertEqual(gender_agg.buckets[0].doc_count, 231)
        self.assertEqual(gender_agg.buckets[0].instance.title, 'Female')
        self.assertEqual(gender_agg.buckets[1].key, 'm')
        self.assertEqual(gender_agg.buckets[1].doc_count, 225)
        self.assertEqual(gender_agg.buckets[1].instance.title, 'Male')
        self.assertEqual(gender_mapper.call_count, 2)
