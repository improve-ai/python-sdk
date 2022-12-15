from copy import deepcopy
import json
import numpy as np
import os
from pytest import fixture, raises
import requests_mock as rqm
import time
from unittest import TestCase
from warnings import catch_warnings, simplefilter

import improveai.decision_model as dm
import improveai.decision_context as dc
from improveai.tests.test_utils import assert_valid_decision, get_test_data, \
    convert_values_to_float32, is_valid_ksuid


class TestDecisionContext(TestCase):

    @property
    def test_decision_model(self):
        return self._test_decision_model

    @test_decision_model.setter
    def test_decision_model(self, value):
        self._test_decision_model = value

    @property
    def valid_test_givens(self):
        return self._valid_test_givens

    @valid_test_givens.setter
    def valid_test_givens(self, value):
        self._valid_test_givens = value

    @property
    def decision_context_test_cases_dir(self):
        return self._decision_context_test_cases_dir

    @decision_context_test_cases_dir.setter
    def decision_context_test_cases_dir(self, value):
        self._decision_context_test_cases_dir = value

    @fixture(autouse=True)
    def prepare_test_artifacts(self):
        self.decision_context_test_cases_dir = os.getenv('DECISION_CONTEXT_TEST_CASES_DIR', None)
        assert self.decision_context_test_cases_dir is not None
        self.test_models_dir = os.getenv('DECISION_MODEL_PREDICTORS_DIR', None)
        assert self.test_models_dir is not None
        self.test_track_url = 'http://mockup.url'
        self.test_decision_model = dm.DecisionModel('dummy-model', track_url=self.test_track_url)
        self.test_decision_model_no_track_url = dm.DecisionModel('dummy-model')
        self.dummy_test_givens = {'a': 1, 'b': '2', 'c': True}

    # - valid variants, invalid givens
    def test_decision_context_invalid_givens(self):
        invalid_test_givens = ['abc', ['a', 'b', 'c'], ('a', 'b', 'c'), 1234, 1234.1234]
        for ig in invalid_test_givens:
            with raises(AssertionError) as aerr:
                dc.DecisionContext(decision_model=self.test_decision_model, context=ig)

    def test_score_valid_list_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=list)

    def test_score_valid_tuple_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=tuple)

    def test_score_valid_nparray_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=np.array)

    def test_score_valid_list_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='score', variants_converter=list)

    def test_score_valid_tuple_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='score', variants_converter=tuple)

    def test_score_valid_nparray_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='score', variants_converter=np.array)

    # - valid variants, {} givens
    def test_score_valid_list_variants_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='score', variants_converter=list)

    def test_score_valid_tuple_variants_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='score', variants_converter=tuple)

    def test_score_valid_nparray_variants_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='score', variants_converter=np.array)

    # - valid variants, None givens
    def test_score_valid_list_variants_none_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_JSON'),
            tested_method_name='score', variants_converter=list)

    def test_score_valid_tuple_variants_none_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_JSON'),
            tested_method_name='score', variants_converter=tuple)

    def test_score_valid_nparray_variants_none_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_JSON'),
            tested_method_name='score', variants_converter=np.array)

    # - valid variants, {} givens
    def test_score_valid_list_variants_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=list)

    def test_score_valid_tuple_variants_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=tuple)

    def test_score_valid_nparray_variants_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=np.array)

    # - valid variants, None givens
    def test_score_valid_list_variants_none_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=list)

    def test_score_valid_tuple_variants_none_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=tuple)

    def test_score_valid_nparray_variants_none_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_NO_MODEL_JSON'),
            tested_method_name='score', variants_converter=np.array)

    # - invalid variants, valid givens
    def test_score_invalid_variants_valid_givens(self):
        invalid_test_variants = ['abc', {'a': 1, 'b': [1, 2, 3], 'c': 'd'}, 1234, 1234.1234]
        valid_givens = {'a': 1, 'b': [1, 2, 3]}
        for iv in invalid_test_variants:
            with raises(AssertionError) as aerr:
                dc.DecisionContext(decision_model=self.test_decision_model, context=valid_givens).score(variants=iv)

    def _generic_test_selected_method(
            self, test_case_json_name, tested_method_name, variants_converter=None):
        path_to_test_json = \
            os.sep.join([self.decision_context_test_cases_dir, test_case_json_name])

        test_case_json = get_test_data(path_to_test_json)

        test_case = test_case_json.get('test_case', None)
        assert test_case is not None

        predictor_filename = test_case.get('model_filename', None)
        if predictor_filename is not None:
            # load model
            model_url = ('{}' + os.sep + '{}').format(self.test_models_dir, predictor_filename)
            self.test_decision_model.load(model_url=model_url)
            self.test_decision_model_no_track_url.load(model_url=model_url)

        # get test variants
        if tested_method_name not in ['choose_multivariate', 'optimize']:
            variants = test_case.get('variants', None)
            assert variants is not None
        else:
            variant_map = test_case.get('variant_map', None)
            assert variant_map is not None

        if variants_converter is not None:
            variants = variants_converter(variants)
        givens = test_case.get('givens', None)
        # assert givens is not None
        scores_seed = test_case_json.get('scores_seed', None)
        assert scores_seed is not None

        expected_output = test_case_json.get('test_output', None)
        assert expected_output is not None

        if tested_method_name != 'rank':
            expected_best = expected_output.get('best', None)
            assert expected_best is not None

        decision_context = dc.DecisionContext(decision_model=self.test_decision_model, context=givens)

        if tested_method_name == 'score':
            np.random.seed(scores_seed)
            scores = decision_context.score(variants=variants)

            test_output = test_case_json.get('test_output', None)
            assert test_output is not None
            expected_scores = test_output.get('scores', None)
            assert expected_scores is not None
            np.testing.assert_array_equal(
                convert_values_to_float32(scores), convert_values_to_float32(expected_scores))

        elif tested_method_name == 'which':
            with rqm.Mocker() as m:
                m.post(self.test_track_url, text='success')

                with catch_warnings(record=True) as w:
                    simplefilter("always")

                    np.random.seed(scores_seed)
                    best, decision_id = decision_context.which(variants)
                    assert best == expected_best
                    assert is_valid_ksuid(decision_id)

                    np.random.seed(scores_seed)
                    best, decision_id = decision_context.which(*variants)
                    assert best == expected_best
                    assert is_valid_ksuid(decision_id)

                    time.sleep(0.175)
                    assert len(w) == 0

        elif tested_method_name == 'rank':
            with rqm.Mocker() as m:
                m.post(self.test_track_url, text='success')

                with catch_warnings(record=True) as w:
                    simplefilter("always")
                    expected_ranked = expected_output.get('ranked_variants', None)
                    assert expected_ranked is not None

                    np.random.seed(scores_seed)
                    calculated_ranked = decision_context.rank(variants=variants)
                    assert decision_context.decision_model.last_decision_id is None
                    np.testing.assert_array_equal(calculated_ranked, expected_ranked)

                    # check that copy of variants is returned
                    assert id(variants) != id(calculated_ranked)

                    # check that input and output is of the same type
                    assert isinstance(calculated_ranked, type(variants))

                    # make sure variants are the same objects
                    sorted_calculated_variants_ids = sorted([id(cv) for cv in calculated_ranked])
                    sorted_input_variants_ids = sorted([id(iv) for iv in variants])
                    np.testing.assert_array_equal(sorted_calculated_variants_ids, sorted_input_variants_ids)

                    # pop input and make sure output's length does not change
                    variants.pop()
                    assert len(variants) == len(calculated_ranked) - 1

                    time.sleep(0.175)
                    assert len(w) == 0

        elif tested_method_name == 'optimize':

            scores_seed = test_case_json.get('scores_seed', None)
            assert scores_seed is not None

            # test with track url != None
            with rqm.Mocker() as m:
                m.post(self.test_track_url, text='success')
                with catch_warnings(record=True) as w:
                    simplefilter("always")
                    decision_context = dc.DecisionContext(
                        decision_model=self.test_decision_model, context=givens)
                    np.random.seed(scores_seed)
                    calculated_best, decision_id = \
                        decision_context.optimize(variant_map=variant_map)
                    assert calculated_best == expected_best
                    assert decision_id is not None
                    assert is_valid_ksuid(decision_id)
                    time.sleep(0.175)
                    assert len(w) == 0

            # test with track url == None
            decision_context = dc.DecisionContext(
                decision_model=self.test_decision_model_no_track_url, context=givens)
            np.random.seed(scores_seed)
            calculated_best, decision_id = \
                decision_context.optimize(variant_map=variant_map)

            assert calculated_best == expected_best

            expected_decision_id = expected_output.get('expected_decision_id')
            assert decision_id == expected_decision_id

        elif tested_method_name == 'choose_multivariate':

            scores_seed = test_case_json.get('scores_seed', None)
            assert scores_seed is not None

            np.random.seed(scores_seed)
            calculated_decision = \
                decision_context.choose_multivariate(variant_map=variant_map)

            assert calculated_decision.best == expected_best

            expected_ranked = expected_output.get('ranked', None)
            assert expected_ranked is not None

            np.testing.assert_array_equal(calculated_decision.ranked, expected_ranked)

            expected_decision_id = expected_output.get('expected_decision_id')
            assert calculated_decision.id_ == expected_decision_id

        elif tested_method_name == 'decide':
            scores = test_case.get("scores", None)
            ordered = test_case.get("ordered", None)

            if ordered is True:
                calculated_decision = decision_context.decide(variants=variants, ordered=ordered)
            elif scores is not None:
                calculated_decision = decision_context.decide(variants=variants, scores=scores)
            else:
                np.random.seed(scores_seed)
                calculated_decision = decision_context.decide(variants=variants)

            for v in calculated_decision.ranked:
                print(v)

            test_output = test_case_json.get('test_output', None)
            assert test_output is not None

            expected_ranked_variants = test_output.get('ranked', None)
            assert expected_ranked_variants is not None

            # check that copy of variants is returned
            assert id(variants) != id(calculated_decision.ranked)

            # check that input and output is of the same type
            assert isinstance(calculated_decision.ranked, type(variants))

            # make sure variants are the same objects
            sorted_calculated_variants_ids = sorted(
                [id(cv) for cv in calculated_decision.ranked])

            sorted_input_variants_ids = sorted([id(iv) for iv in variants])
            np.testing.assert_array_equal(sorted_calculated_variants_ids,
                                          sorted_input_variants_ids)

            # pop input and make sure output's length does not change
            variants.pop()
            assert len(variants) == len(calculated_decision.ranked) - 1

            np.testing.assert_array_equal(calculated_decision.ranked, expected_ranked_variants)
            assert calculated_decision.best == expected_best
        else:
            raise ValueError(f'tested_method_name: {tested_method_name} not suported')

    def test_which_valid_list_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='which', variants_converter=list)

    def test_which_valid_tuple_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='which', variants_converter=tuple)

    def test_which_valid_ndarray_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='which', variants_converter=np.array)

    def test_which_valid_list_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=list)

    def test_which_valid_tuple_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=tuple)

    def test_which_valid_ndarray_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=np.array)

    def test_which_valid_list_variants_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='which', variants_converter=list)

    def test_which_valid_tuple_variants_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='which', variants_converter=tuple)

    def test_which_valid_ndarray_variants_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='which', variants_converter=np.array)

    def test_which_valid_list_variants_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=list)

    def test_which_valid_tuple_variants_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=tuple)

    def test_which_valid_ndarray_variants_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=np.array)

    def test_which_valid_list_variants_none_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_JSON'),
            tested_method_name='which', variants_converter=list)

    def test_which_valid_tuple_variants_none_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_JSON'),
            tested_method_name='which', variants_converter=tuple)

    def test_which_valid_ndarray_variants_none_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_JSON'),
            tested_method_name='which', variants_converter=np.array)

    def test_which_valid_list_variants_none_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=list)

    def test_which_valid_tuple_variants_none_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=tuple)

    def test_which_valid_ndarray_variants_none_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_VALID_VARIANTS_NONE_GIVENS_NO_MODEL_JSON'),
            tested_method_name='which', variants_converter=np.array)

    # - invalid variants, valid givens
    def test_which_invalid_variants_valid_givens_raises(self):
        invalid_test_variants = ['abc', {'a': 1, 'b': [1, 2, 3], 'c': 'd'}, 1234, 1234.1234]
        valid_givens = {'a': 1, 'b': [1, 2, 3]}
        for iv in invalid_test_variants:
            with rqm.Mocker() as m:
                m.post(self.test_track_url, text='success')
                with raises(AssertionError) as aerr:
                    dc.DecisionContext(decision_model=self.test_decision_model, context=valid_givens).which(*[iv])

    # - invalid variants, valid givens
    def test_which_empty_variants_valid_givens_raises(self):
        invalid_test_variants = [[], tuple([]), np.array([])]
        valid_givens = {'a': 1, 'b': [1, 2, 3]}
        for iv in invalid_test_variants:
            with rqm.Mocker() as m:
                m.post(self.test_track_url, text='success')
                with raises(AssertionError):
                    dc.DecisionContext(decision_model=self.test_decision_model, context=valid_givens).which(*iv)

    def test_which_none_track_url(self):
        model = dm.DecisionModel(model_name='dummy-model', track_url=None)
        chosen_variant, decision_id = dc.DecisionContext(decision_model=model, context=None).which(1, 2, 3, 4, 5)
        # make sure which did not track decision
        assert decision_id is None
        assert chosen_variant == 1

    def test_which_from_none_track_url(self):
        model = dm.DecisionModel(model_name='dummy-model', track_url=None)
        chosen_variant, decision_id = dc.DecisionContext(decision_model=model, context=None)\
            .which_from(variants=[1, 2, 3, 4, 5])

        # make sure which did not track decision
        assert decision_id is None
        assert chosen_variant == 1

    def test_rank_no_model(self):
        # test_case_json_name, tested_method_name, variants_converter=None
        self._generic_test_selected_method(
            test_case_json_name=os.getenv(
                'DECISION_CONTEXT_TEST_RANK_NATIVE_NO_MODEL_JSON'),
            tested_method_name='rank', variants_converter=None)

    def test_rank(self):
        self._generic_test_selected_method(
            test_case_json_name=os.getenv(
                'DECISION_CONTEXT_TEST_RANK_NATIVE_JSON'),
            tested_method_name='rank', variants_converter=None)

    def test_rank_no_track_url(self):
        model = dm.DecisionModel('test-model')
        ranked_variants = model.rank([1, 2, 3, 4])
        # make sure call was not tracked
        assert model.last_decision_id is None
        np.testing.assert_array_equal(ranked_variants, [1, 2, 3, 4])

    def test_track(self):
        decision_model = dm.DecisionModel('dummy-model', track_url=self.test_track_url)
        decision_context = \
            dc.DecisionContext(decision_model=decision_model, context=self.dummy_test_givens)
        decision_tracker = decision_model.tracker
        decision_tracker.max_runners_up = 5

        variant = 1
        runners_up = [2, 3, 4, 5, 6]
        sample = 7
        sample_pool_size = 10

        expected_track_body = {
            decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
            decision_tracker.MODEL_KEY: decision_model.model_name,
            decision_tracker.VARIANT_KEY: variant,
            decision_tracker.VARIANTS_COUNT_KEY: 16,
            decision_tracker.RUNNERS_UP_KEY: runners_up,
            decision_tracker.SAMPLE_KEY: sample,
            decision_tracker.GIVENS_KEY: self.dummy_test_givens
        }

        expected_request_json = json.dumps(expected_track_body, sort_keys=False)

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[decision_tracker.MESSAGE_ID_KEY]

            if json.dumps(request_dict, sort_keys=False) != \
                    expected_request_json:

                print('raw request body:')
                print(request.text)
                print('compared request string')
                print(json.dumps(request_dict, sort_keys=False))
                print('expected body:')
                print(expected_request_json)
                return None
            return True

        tracks_runners_up_seed = os.getenv('DECISION_TRACKER_TRACKS_SEED', None)

        assert tracks_runners_up_seed is not None

        with rqm.Mocker() as m:
            m.post(self.test_track_url, text='success', additional_matcher=custom_matcher)
            with catch_warnings(record=True) as w:
                simplefilter("always")
                decision_id = decision_context._track(
                    variant=variant, runners_up=runners_up, sample=sample,
                    sample_pool_size=sample_pool_size)
                is_valid_ksuid(decision_id)
                time.sleep(0.175)
                assert len(w) == 0

    def test_track_no_runners_up(self):
        decision_model = dm.DecisionModel('dummy-model', track_url=self.test_track_url)
        decision_context = \
            dc.DecisionContext(decision_model=decision_model, context=self.dummy_test_givens)
        decision_tracker = decision_model.tracker
        decision_tracker.max_runners_up = 0

        variant = 1
        runners_up = None
        sample = 7
        sample_pool_size = 10

        expected_track_body = {
            decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
            decision_tracker.MODEL_KEY: decision_model.model_name,
            decision_tracker.VARIANT_KEY: variant,
            decision_tracker.VARIANTS_COUNT_KEY: 11,
            decision_tracker.SAMPLE_KEY: sample,
            decision_tracker.GIVENS_KEY: self.dummy_test_givens
        }

        expected_request_json = json.dumps(expected_track_body, sort_keys=False)

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[decision_tracker.MESSAGE_ID_KEY]

            if json.dumps(request_dict, sort_keys=False) != \
                    expected_request_json:

                print('raw request body:')
                print(request.text)
                print('compared request string')
                print(json.dumps(request_dict, sort_keys=False))
                print('expected body:')
                print(expected_request_json)
                return None
            return True

        tracks_runners_up_seed = os.getenv('DECISION_TRACKER_TRACKS_SEED', None)

        assert tracks_runners_up_seed is not None

        with rqm.Mocker() as m:
            m.post(self.test_track_url, text='success', additional_matcher=custom_matcher)
            with catch_warnings(record=True) as w:
                simplefilter("always")
                decision_id = decision_context._track(
                    variant=variant, runners_up=runners_up, sample=sample,
                    sample_pool_size=sample_pool_size)
                is_valid_ksuid(decision_id)
                time.sleep(0.175)
                assert len(w) == 0

    def test_track_no_sample(self):
        decision_model = dm.DecisionModel('dummy-model', track_url=self.test_track_url)
        decision_context = \
            dc.DecisionContext(decision_model=decision_model, context=self.dummy_test_givens)
        decision_tracker = decision_model.tracker
        decision_tracker.max_runners_up = 5

        variant = 1
        runners_up = [2, 3, 4, 5, 6]
        sample = None
        sample_pool_size = 0

        expected_track_body = {
            decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
            decision_tracker.MODEL_KEY: decision_model.model_name,
            decision_tracker.VARIANT_KEY: variant,
            decision_tracker.VARIANTS_COUNT_KEY: 6,
            decision_tracker.RUNNERS_UP_KEY: runners_up,
            decision_tracker.GIVENS_KEY: self.dummy_test_givens
        }

        expected_request_json = json.dumps(expected_track_body, sort_keys=False)

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[decision_tracker.MESSAGE_ID_KEY]

            if json.dumps(request_dict, sort_keys=False) != \
                    expected_request_json:

                print('raw request body:')
                print(request.text)
                print('compared request string')
                print(json.dumps(request_dict, sort_keys=False))
                print('expected body:')
                print(expected_request_json)
                return None
            return True

        tracks_runners_up_seed = os.getenv('DECISION_TRACKER_TRACKS_SEED', None)

        assert tracks_runners_up_seed is not None

        with rqm.Mocker() as m:
            m.post(self.test_track_url, text='success', additional_matcher=custom_matcher)
            with catch_warnings(record=True) as w:
                simplefilter("always")
                decision_id = decision_context._track(
                    variant=variant, runners_up=runners_up, sample=sample,
                    sample_pool_size=sample_pool_size)
                is_valid_ksuid(decision_id)
                time.sleep(0.175)
                assert len(w) == 0

    def test_track_no_runners_up_no_sample(self):
        decision_model = dm.DecisionModel('dummy-model', track_url=self.test_track_url)
        decision_context = \
            dc.DecisionContext(decision_model=decision_model, context=self.dummy_test_givens)
        decision_tracker = decision_model.tracker
        decision_tracker.max_runners_up = 5

        variant = 1
        runners_up = None
        sample = None
        sample_pool_size = 0

        expected_track_body = {
            decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
            decision_tracker.MODEL_KEY: decision_model.model_name,
            decision_tracker.VARIANT_KEY: variant,
            decision_tracker.VARIANTS_COUNT_KEY: 1,
            decision_tracker.GIVENS_KEY: self.dummy_test_givens
        }

        expected_request_json = json.dumps(expected_track_body, sort_keys=False)

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[decision_tracker.MESSAGE_ID_KEY]

            if json.dumps(request_dict, sort_keys=False) != \
                    expected_request_json:

                print('raw request body:')
                print(request.text)
                print('compared request string')
                print(json.dumps(request_dict, sort_keys=False))
                print('expected body:')
                print(expected_request_json)
                return None
            return True

        tracks_runners_up_seed = os.getenv('DECISION_TRACKER_TRACKS_SEED', None)

        assert tracks_runners_up_seed is not None

        with rqm.Mocker() as m:
            m.post(self.test_track_url, text='success', additional_matcher=custom_matcher)
            with catch_warnings(record=True) as w:
                simplefilter("always")
                decision_id = decision_context._track(
                    variant=variant, runners_up=runners_up, sample=sample,
                    sample_pool_size=sample_pool_size)
                is_valid_ksuid(decision_id)
                time.sleep(0.175)
                assert len(w) == 0

    def test_track_raises_for_empty_runners_up(self):
        decision_model = dm.DecisionModel('dummy-model', track_url=self.test_track_url)
        decision_context = \
            dc.DecisionContext(decision_model=decision_model, context=self.dummy_test_givens)
        with raises(AssertionError):
            decision_context._track(
                variant=1, runners_up=[], sample=2, sample_pool_size=2)

    def test_track_raises_for_no_track_url(self):
        decision_model = dm.DecisionModel('dummy-model')
        decision_context = \
            dc.DecisionContext(decision_model=decision_model, context=self.dummy_test_givens)
        with raises(AssertionError) as aeerr:
            decision_context._track(
                variant=1, runners_up=[1, 2, 3], sample=2, sample_pool_size=2)

    # TODO test optimize
    def test_optimize_empty_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_OPTIMIZE_CHOOSE_MULTIVARIATE_VALID_VARIANTS_EMPTY_GIVENS_NO_MODEL_JSON'),
            tested_method_name='optimize')

    # TODO test optimize
    def test_optimize_empty_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_OPTIMIZE_CHOOSE_MULTIVARIATE_VALID_VARIANTS_EMPTY_GIVENS_JSON'),
            tested_method_name='optimize')

    # TODO test optimize
    def test_optimize_valid_variants_valid_givens(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_OPTIMIZE_CHOOSE_MULTIVARIATE_VALID_VARIANTS_VALID_GIVENS_JSON'),
            tested_method_name='optimize')

    # TODO test optimize
    def test_optimize_valid_variants_valid_givens_no_model(self):
        self._generic_test_selected_method(
            os.getenv('DECISION_CONTEXT_OPTIMIZE_CHOOSE_MULTIVARIATE_VALID_VARIANTS_VALID_GIVENS_NO_MODEL_JSON'),
            tested_method_name='optimize')

    def test_optimize_raises_for_empty_variant_map(self):
        decision_context = dc.DecisionContext(decision_model=self.test_decision_model, context=None)
        with raises(AssertionError) as aerr:
            decision_context.optimize({})

    def test_optimize_raises_for_none_variant_map(self):
        decision_context = dc.DecisionContext(decision_model=self.test_decision_model, context=None)
        with raises(AssertionError) as aerr:
            decision_context.optimize(None)

    def test_optimize_raises_for_wrong_variant_map_type(self):
        decision_context = dc.DecisionContext(decision_model=self.test_decision_model, context=None)
        with raises(AssertionError) as aerr:
            decision_context.optimize([1, 2, 3])

    def test_optimize_raises_for_one_empty_entry_in_variant_map(self):
        decision_context = dc.DecisionContext(decision_model=self.test_decision_model, context=None)
        with raises(AssertionError) as verr:
            decision_context.optimize({'a': [], 'b': [1, 2, 3]})

    def test_decide_valid_model_no_scores_not_ordered_no_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_VALID_MODEL_NO_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_no_model_no_scores_not_ordered_no_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_NO_MODEL_NO_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_no_scores_ordered_no_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_VALID_MODEL_NO_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_no_model_no_scores_ordered_no_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_NO_MODEL_NO_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_scores_not_ordered_no_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_VALID_MODEL_NO_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_no_model_scores_not_ordered_no_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_NO_MODEL_NO_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_no_scores_not_ordered_valid_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_no_model_no_scores_not_ordered_valid_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_NO_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_no_scores_ordered_valid_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_no_model_no_scores_ordered_valid_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_NO_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_scores_not_ordered_valid_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_no_model_scores_not_ordered_valid_givens(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_NO_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_bool_variants_no_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_BOOL_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_bool_variants_no_scores_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_BOOL_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_bool_variants_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_BOOL_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_dict_variants_no_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_DICT_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_dict_variants_no_scores_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_DICT_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_dict_variants_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_DICT_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_float_variants_no_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_FLOAT_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_float_variants_no_scores_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_FLOAT_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_float_variants_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_FLOAT_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_int_variants_no_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_INT_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_int_variants_no_scores_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_INT_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_int_variants_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_INT_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_lists_variants_no_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_LISTS_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_lists_variants_no_scores_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_LISTS_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_lists_variants_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_LISTS_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_string_variants_no_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_STRING_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_string_variants_no_scores_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_STRING_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def test_decide_valid_model_string_variants_scores_not_ordered(self):
        test_case_json_filename = os.getenv('DECISION_CONTEXT_TEST_DECIDE_STRING_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON')
        self._generic_test_selected_method(test_case_json_filename, 'decide', variants_converter=None)

    def _generic_test_decide_valid_model_tuple_variants(self, test_case_json_name):

        path_to_test_json = \
            os.sep.join(
                [self.decision_context_test_cases_dir, test_case_json_name])

        test_case_json = get_test_data(path_to_test_json)

        test_case = test_case_json.get('test_case', None)
        assert test_case is not None

        predictor_filename = test_case.get('model_filename', None)
        assert predictor_filename is not None

        if predictor_filename is not None:
            # load model
            model_url = ('{}' + os.sep + '{}').format(self.test_models_dir,
                                                      predictor_filename)
            self.test_decision_model.load(model_url=model_url)
            self.test_decision_model_no_track_url.load(model_url=model_url)

        # get test variants
        variants = test_case.get('variants', None)
        assert variants is not None
        variants = [tuple(variant) for variant in variants]
        print('### variants ###')
        print(variants)

        givens = test_case.get('givens', None)

        scores_seed = test_case_json.get('scores_seed', None)
        assert scores_seed is not None

        expected_output = test_case_json.get('test_output', None)
        assert expected_output is not None

        expected_best = expected_output.get('best', None)
        assert expected_best is not None
        expected_best = tuple(expected_best)

        decision_context = dc.DecisionContext(
            decision_model=self.test_decision_model, context=givens)

        scores = test_case.get("scores", None)
        ordered = test_case.get("ordered", None)

        if ordered is True:
            calculated_decision = decision_context.decide(variants=variants,
                                                          ordered=ordered)
        elif scores is not None:
            calculated_decision = decision_context.decide(variants=variants,
                                                          scores=scores)
        else:
            np.random.seed(scores_seed)
            calculated_decision = decision_context.decide(variants=variants)

        print('### calculated decision ranked ###')
        for v in calculated_decision.ranked:
            print(v)

        test_output = test_case_json.get('test_output', None)
        assert test_output is not None

        expected_ranked_variants = test_output.get('ranked', None)
        assert expected_ranked_variants is not None

        expected_ranked_variants = [tuple(variant) for variant in
                                    expected_ranked_variants]
        print('### expected_ranked_variants ###')
        print(expected_ranked_variants)

        # check that copy of variants is returned
        assert id(variants) != id(calculated_decision.ranked)

        # check that input and output is of the same type
        assert isinstance(calculated_decision.ranked, type(variants))

        # make sure variants are the same objects
        sorted_calculated_variants_ids = sorted(
            [id(cv) for cv in calculated_decision.ranked])

        sorted_input_variants_ids = sorted([id(iv) for iv in variants])
        np.testing.assert_array_equal(sorted_calculated_variants_ids,
                                      sorted_input_variants_ids)

        # pop input and make sure output's length does not change
        variants.pop()
        assert len(variants) == len(calculated_decision.ranked) - 1

        np.testing.assert_array_equal(calculated_decision.ranked,
                                      expected_ranked_variants)
        assert calculated_decision.best == expected_best

    # TODO test with tuple variants
    def test_decide_valid_model_tuple_variants_no_scores_not_ordered(self):
        test_case_json_name = os.getenv('DECISION_CONTEXT_TEST_DECIDE_LISTS_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_NOT_ORDERED_JSON', None)
        assert test_case_json_name is not None
        self._generic_test_decide_valid_model_tuple_variants(test_case_json_name)

    def test_decide_valid_model_tuple_variants_no_scores_ordered(self):
        test_case_json_name = os.getenv(
            'DECISION_CONTEXT_TEST_DECIDE_LISTS_VARIANTS_VALID_MODEL_VALID_GIVENS_NO_SCORES_ORDERED_JSON', None)
        assert test_case_json_name is not None
        self._generic_test_decide_valid_model_tuple_variants(test_case_json_name)

    def test_decide_valid_model_tuple_variants_scores_not_ordered(self):
        test_case_json_name = os.getenv(
            'DECISION_CONTEXT_TEST_DECIDE_LISTS_VARIANTS_VALID_MODEL_VALID_GIVENS_SCORES_NOT_ORDERED_JSON', None)
        assert test_case_json_name is not None
        self._generic_test_decide_valid_model_tuple_variants(test_case_json_name)

    def test_decide_raises_for_variants_and_scores_different_length(self):
        context = dc.DecisionContext(decision_model=self.test_decision_model_no_track_url, context={})
        variants = [1, 2, 3]
        scores = [0.1, 0.2, 0.3, 0.4]

        with raises(AssertionError) as aerr:
            context.decide(variants=variants, scores=scores)

    def test_decide_raises_for_bad_ordered_type(self):
        model = dm.DecisionModel(model_name='dummy-model')
        context = dc.DecisionContext(decision_model=self.test_decision_model_no_track_url, context={})
        variants = [1, 2, 3]

        with raises(AssertionError) as aerr:
            context.decide(variants=variants, ordered=None)

        with raises(AssertionError) as aerr:
            context.decide(variants=variants, ordered='True')

        with raises(AssertionError) as aerr:
            context.decide(variants=variants, ordered=1)

        with raises(AssertionError) as aerr:
            context.decide(variants=variants, ordered=1.123)

    def test_decide_raises_for_bad_variants(self):
        context = dc.DecisionContext(decision_model=self.test_decision_model_no_track_url, context={})

        with raises(AssertionError) as aerr:
            variants = 1
            context.decide(variants=variants, ordered=None)

        with raises(AssertionError) as aerr:
            variants = 1.123
            context.decide(variants=variants, ordered=None)

        with raises(AssertionError) as aerr:
            variants = 'string'
            context.decide(variants=variants, ordered=None)

        with raises(AssertionError) as aerr:
            variants = True
            context.decide(variants=variants, ordered=None)

        with raises(AssertionError) as aerr:
            variants = {'test-dict': 123}
            context.decide(variants=variants, ordered=None)

    def test_decide_with_ndarray_variants(self):
        context = dc.DecisionContext(decision_model=self.test_decision_model_no_track_url, context={})
        variants = np.array([1, 2, 3])

        decision = context.decide(variants=variants)
        np.testing.assert_array_equal(variants, decision.ranked)

    def test_decide_with_tuple_variants(self):
        context = dc.DecisionContext(decision_model=self.test_decision_model_no_track_url, context={})
        variants = (1, 2, 3)

        decision = context.decide(variants=variants)
        np.testing.assert_array_equal(variants, decision.ranked)

    def test_decide_raises_for_scores_and_ordered_true(self):
        model = dm.DecisionModel(model_name='dummy-model')

        with raises(ValueError) as verr:
            model.decide(variants=[1, 2, 3], scores=[1, 2, 3], ordered=True)

    def test_decide_input_variants_not_mutated_after_decision_creation_no_model(self):
        context = dc.DecisionContext(decision_model=self.test_decision_model_no_track_url, context={})
        variants = [1, 2, 3]
        expected_ranked_variants = list(reversed(variants))
        decision = context.decide(variants=variants, scores=[1, 2, 3])
        np.testing.assert_array_equal(decision.ranked, expected_ranked_variants)
        np.testing.assert_array_equal(variants, [1, 2, 3])

    def test_decide_input_variants_not_mutated_after_decision_creation(self):
        model = dm.DecisionModel('test-model')

        model_url = os.getenv('DUMMY_MODEL_PATH', None)
        assert model_url is not None

        model.load(model_url=model_url)

        context = dc.DecisionContext(decision_model=model, context={})

        variants = [{'text': 'lovely corgi'}, {'text': 'bad swan'}, {'text': 'fat hippo'}]
        np.random.seed(1)
        decision = context.decide(variants=variants)
        expected_ranked_variants = [{'text': 'lovely corgi'}, {'text': 'fat hippo'}, {'text': 'bad swan'}]
        np.testing.assert_array_equal(decision.ranked, expected_ranked_variants)
        np.testing.assert_array_equal(variants, [{'text': 'lovely corgi'}, {'text': 'bad swan'}, {'text': 'fat hippo'}])

