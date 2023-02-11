import time
from copy import deepcopy
import json
from ksuid import Ksuid
import math
import numpy as np
import requests_mock as rqm
import os
from pytest import fixture, raises
import sys
from warnings import catch_warnings, simplefilter

sys.path.append(
    os.sep.join(str(os.path.abspath(__file__)).split(os.sep)[:-3]))

import improveai
import improveai.reward_tracker as rtr
from improveai.settings import MAX_TRACK_THREADS
from improveai.utils.general_purpose_tools import is_valid_ksuid


class TestRewardTracker:

    @property
    def tracks_seed(self) -> int:
        return self._tracks_seed

    @tracks_seed.setter
    def tracks_seed(self, value: int):
        self._tracks_seed = value

    @property
    def not_tracks_seed(self):
        return self._not_tracks_seed

    @not_tracks_seed.setter
    def not_tracks_seed(self, value):
        self._not_tracks_seed = value

    @property
    def not_tracks_seed_1(self):
        return self._not_tracks_seed_1

    @not_tracks_seed_1.setter
    def not_tracks_seed_1(self, value):
        self._not_tracks_seed_1 = value

    @property
    def track_url(self) -> str:
        return self._track_url

    @track_url.setter
    def track_url(self, value: str):
        self._track_url = value

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = value

    @property
    def variants_count(self):
        return self._variants_count

    @variants_count.setter
    def variants_count(self, value):
        self._variants_count = value

    @property
    def candidates(self):
        return self._variants

    @candidates.setter
    def candidates(self, value):
        self._variants = value
        
    @property
    def max_runners_up(self):
        return self._max_runners_up

    @max_runners_up.setter
    def max_runners_up(self, value):
        self._max_runners_up = value

    @property
    def sample_seed(self):
        return self._sample_seed

    @sample_seed.setter
    def sample_seed(self, value):
        self._sample_seed = value

    @fixture(autouse=True)
    def prep_env(self):

        self.track_url = os.getenv('REWARD_TRACKER_TEST_URL')
        self.api_key = os.getenv('REWARD_TRACKER_TEST_API_KEY')
        self.sample_seed = int(os.getenv('REWARD_TRACKER_SAMPLE_SEED'))

        self.candidates = list(range(100))

        self.dummy_item = {'dummy0': 'item'}
        self.dummy_context = {'dummy1': 'context'}
        self.dummy_candidates = \
            np.array(
                [self.dummy_item] +
                [{'dummy{}'.format(el): 'item'}
                 for el in range(1, len(self.candidates))])

        self.dummy_model_name = 'dummy-model'
        self.dummy_message_id = 'dummy_message'
        self.reward_tracker = rtr.RewardTracker(
            model_name=self.dummy_model_name, track_url=self.track_url,
            _threaded_requests=False)

    # TODO test _get_track_body()
    def test__get_track_body_1_candidate_no_sample_no_context(self):
        # reward_tracker = rtr.RewardTracker(
        #     model_name=self.dummy_model_name, track_url=self.track_url)
        calculated_body = self.reward_tracker._get_track_body(
            item=self.dummy_item, num_candidates=1, context=None, sample=None)
        expected_body = {
            # self.reward_tracker.TYPE_KEY: self.reward_tracker.DECISION_TYPE,
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: self.dummy_item,
            self.reward_tracker.ITEMS_COUNT_KEY: 1}
        assert calculated_body == expected_body
        # for key in expected_body.keys():
        #     assert id(expected_body[key]) != id(calculated_body[key])

    def test__get_track_body_2_candidate_no_context(self):
        # reward_tracker = rtr.RewardTracker(model_name=self.dummy_model_name, track_url=self.track_url)
        calculated_body = self.reward_tracker._get_track_body(
            item=self.dummy_item, num_candidates=2, context=None, sample=2)
        expected_body = {
            # self.reward_tracker.TYPE_KEY: self.reward_tracker.DECISION_TYPE,
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: self.dummy_item,
            self.reward_tracker.ITEMS_COUNT_KEY: 2,
            self.reward_tracker.SAMPLE_KEY: 2}
        assert calculated_body == expected_body
        # for key in expected_body.keys():
        #     assert id(expected_body[key]) != id(calculated_body[key])

    def test__get_track_body_2_candidate(self):
        # reward_tracker = rtr.RewardTracker(model_name=self.dummy_model_name, track_url=self.track_url)
        calculated_body = self.reward_tracker._get_track_body(
            item=self.dummy_item, num_candidates=2, context=self.dummy_context, sample=2)
        expected_body = {
            # self.reward_tracker.TYPE_KEY: self.reward_tracker.DECISION_TYPE,
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: self.dummy_item,
            self.reward_tracker.ITEMS_COUNT_KEY: 2,
            self.reward_tracker.SAMPLE_KEY: 2,
            self.reward_tracker.CONTEXT_KEY: self.dummy_context}
        assert calculated_body == expected_body
        # for key in expected_body.keys():
        #     assert id(expected_body[key]) != id(calculated_body[key])

    # # TODO test _get_sample()
    def test__get_sample_2_candidates(self):
        candidates = [self.dummy_item, 'abc']
        calculated_sample = self.reward_tracker._get_sample(item=self.dummy_item, candidates=candidates)
        expected_sample = 'abc'
        assert calculated_sample == expected_sample

    def test__get_sample_many_candidates(self):
        np.random.seed(self.sample_seed)
        calculated_sample = \
            self.reward_tracker._get_sample(item=self.dummy_item, candidates=list(self.dummy_candidates))
        expected_sample = {'dummy40': 'item'}
        assert calculated_sample == expected_sample

    def test__get_sample_many_candidates_array(self):
        np.random.seed(self.sample_seed)
        calculated_sample = \
            self.reward_tracker._get_sample(item=self.dummy_item, candidates=list(self.dummy_candidates))
        expected_sample = {'dummy40': 'item'}
        assert calculated_sample == expected_sample

    def test__get_sample_raises_for_1_el_candidates(self):
        with raises(AssertionError) as aerr:
            self.reward_tracker._get_sample(item=self.dummy_item, candidates=[self.dummy_item])
            if not aerr.value:
                raise ValueError('No AssertionError raised')

    def test__get_sample_2_candidates_duplicates(self):
        candidates = [self.dummy_item, self.dummy_item]
        calculated_sample = self.reward_tracker._get_sample(
            item=self.dummy_item, candidates=candidates)
        expected_sample = self.dummy_item
        assert calculated_sample == expected_sample

    def test_track_single_none_item_none_context_no_runners_up(self):

        expected_track_body = {
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: None,
            self.reward_tracker.ITEMS_COUNT_KEY: 1,
        }

        expected_request_json = json.dumps(expected_track_body, sort_keys=False)

        def custom_matcher(request):

            request_dict = deepcopy(request.json())
            del request_dict[self.reward_tracker.MESSAGE_ID_KEY]

            if json.dumps(request_dict, sort_keys=False) != expected_request_json:

                print('request body:')
                print(request.text)
                print('expected body:')
                print(expected_request_json)
                return None
            return True

        with rqm.Mocker() as m:
            m.post(self.track_url, text='success',
                   additional_matcher=custom_matcher)

            with catch_warnings(record=True) as w:
                simplefilter("always")
                # item: object, num_candidates: int, context: object, sample
                reward_id = self.reward_tracker.track(item=None, candidates=[None], context=None)
                time.sleep(0.175)
                assert len(w) == 0

            assert is_valid_ksuid(reward_id)

    def test_track_none_context(self):

        candidates = [el for el in range(1, 20, 1)]
        expected_sample = 9

        expected_track_body = {
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: candidates[0],
            self.reward_tracker.ITEMS_COUNT_KEY: len(candidates),
            self.reward_tracker.SAMPLE_KEY: expected_sample}

        posted_request_container = {'request_json': None}

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[self.reward_tracker.MESSAGE_ID_KEY]
            posted_request_container['request_json'] = request_dict
            return True

        with rqm.Mocker() as m:
            m.post(self.track_url, text='success',
                   additional_matcher=custom_matcher)

            with catch_warnings(record=True) as w:
                simplefilter("always")
                np.random.seed(self.sample_seed)
                reward_id = self.reward_tracker.track(item=candidates[0], candidates=candidates, context=None)
                time.sleep(0.175)
                assert len(w) == 0

            assert is_valid_ksuid(reward_id)
            assert posted_request_container['request_json'] == expected_track_body

    def test_track_2_variants_no_context(self):

        candidates = [0, 1]
        item = candidates[0]

        expected_track_body = {
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: item,
            self.reward_tracker.ITEMS_COUNT_KEY: len(candidates),
            self.reward_tracker.SAMPLE_KEY: candidates[1]}

        posted_request_container = {'request_json': None}

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[self.reward_tracker.MESSAGE_ID_KEY]
            posted_request_container['request_json'] = request_dict
            return True

        with rqm.Mocker() as m:
            m.post(self.track_url, text='success',
                   additional_matcher=custom_matcher)

            with catch_warnings(record=True) as w:
                simplefilter("always")
                np.random.seed(self.sample_seed)
                reward_id = self.reward_tracker.track(item=item, candidates=candidates, context=None)
                time.sleep(0.175)
                assert len(w) == 0

            assert is_valid_ksuid(reward_id)
            assert posted_request_container['request_json'] == expected_track_body

    def test_track(self):

        candidates = [el for el in range(1, 20, 1)]
        item = candidates[0]
        context = {'dummy': 'givens'}
        expected_sample = 6

        expected_track_body = {
            self.reward_tracker.MODEL_KEY: self.dummy_model_name,
            self.reward_tracker.ITEM_KEY: item,
            self.reward_tracker.ITEMS_COUNT_KEY: len(candidates),
            self.reward_tracker.SAMPLE_KEY: expected_sample,
            self.reward_tracker.CONTEXT_KEY: context}

        posted_request_container = {'request_json': None}

        def custom_matcher(request):
            request_dict = deepcopy(request.json())
            del request_dict[self.reward_tracker.MESSAGE_ID_KEY]
            posted_request_container['request_json'] = request_dict
            return True

        with rqm.Mocker() as m:
            m.post(self.track_url, text='success',
                   additional_matcher=custom_matcher)

            with catch_warnings(record=True) as w:
                simplefilter("always")
                np.random.seed(self.sample_seed)
                np.random.seed(1)
                reward_id = self.reward_tracker.track(item=item, candidates=candidates, context=context)
                time.sleep(0.175)
                assert len(w) == 0
            # raise

            assert is_valid_ksuid(reward_id)
            assert posted_request_container['request_json'] == expected_track_body

    # def test_track_ndarray_variants(self):
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     variants = [el for el in range(1, 20, 1)]
    #     top_runners_up = variants[1:self.max_runners_up + 1]
    #     givens = {'dummy': 'givens'}
    #     expected_sample = 18
    #
    #     expected_track_body = {
    #         decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
    #         decision_tracker.MODEL_KEY: self.dummy_model_name,
    #         decision_tracker.ITEM_KEY: variants[0],
    #         decision_tracker.ITEMS_COUNT_KEY: len(variants),
    #         decision_tracker.RUNNERS_UP_KEY: top_runners_up,
    #         decision_tracker.SAMPLE_KEY: expected_sample,
    #         decision_tracker.CONTEXT_KEY: givens}
    #
    #     expected_request_json = json.dumps(expected_track_body, sort_keys=False)
    #
    #     def custom_matcher(request):
    #         request_dict = deepcopy(request.json())
    #         del request_dict[decision_tracker.MESSAGE_ID_KEY]
    #
    #         if json.dumps(request_dict, sort_keys=False) != \
    #                 expected_request_json:
    #
    #             print('request body:')
    #             print(request.text)
    #             print('expected body:')
    #             print(expected_request_json)
    #             return None
    #         return True
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher)
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.tracks_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=np.array(variants),
    #                 givens=givens, model_name=self.dummy_model_name)
    #         time.sleep(0.175)
    #         assert len(w) == 0
    #
    #     assert is_valid_ksuid(decision_id)
    #
    # def test_track_2_variants_and_sample(self):
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     variants = [el for el in range(1, 3, 1)]
    #     top_runners_up = variants[1:]
    #
    #     expected_track_body = {
    #         decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
    #         decision_tracker.MODEL_KEY: self.dummy_model_name,
    #         decision_tracker.ITEM_KEY: variants[0],
    #         decision_tracker.ITEMS_COUNT_KEY: len(variants),
    #         decision_tracker.RUNNERS_UP_KEY: top_runners_up,
    #     }
    #
    #     expected_request_json = json.dumps(expected_track_body, sort_keys=False)
    #
    #     def custom_matcher(request):
    #         request_dict = deepcopy(request.json())
    #         del request_dict[decision_tracker.MESSAGE_ID_KEY]
    #
    #         if json.dumps(request_dict, sort_keys=False) != \
    #                 expected_request_json:
    #
    #             print('request body:')
    #             print(request.text)
    #             print('expected body:')
    #             print(expected_request_json)
    #             return None
    #         return True
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    # def test_track_2_variants_max_runners_up_0(self):
    #
    #     max_runners_up = 0
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = max_runners_up
    #
    #     variants = [el for el in range(1, 3, 1)]
    #     expected_sample = variants[1]
    #
    #     expected_track_body = {
    #         decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
    #         decision_tracker.MODEL_KEY: self.dummy_model_name,
    #         decision_tracker.ITEM_KEY: variants[0],
    #         decision_tracker.ITEMS_COUNT_KEY: len(variants),
    #         decision_tracker.SAMPLE_KEY: expected_sample
    #     }
    #
    #     expected_request_json = json.dumps(expected_track_body, sort_keys=False)
    #
    #     def custom_matcher(request):
    #         request_dict = deepcopy(request.json())
    #         del request_dict[decision_tracker.MESSAGE_ID_KEY]
    #
    #         if json.dumps(request_dict, sort_keys=False) != \
    #                 expected_request_json:
    #
    #             print('request body:')
    #             print(request.text)
    #             print('expected body:')
    #             print(expected_request_json)
    #             return None
    #         return True
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    # def test_should_track_runners_up_2_variants_1(self):
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     assert all(
    #         [decision_tracker._should_track_runners_up(variants_count=2)
    #          for _ in range(10)])
    #
    # def test_top_runners_up_2_variants(self):
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     variants = [el for el in range(2)]
    #
    #     top_runners_up = decision_tracker._top_runners_up(ranked_variants=variants)
    #
    #     assert top_runners_up == [1]
    #
    # def test_track_2_variants_no_sample_max_runners_up_50(self):
    #
    #     max_runners_up = 50
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = max_runners_up
    #
    #     variants = [el for el in range(0, 1)]
    #
    #     expected_track_body = {
    #         decision_tracker.TYPE_KEY: decision_tracker.DECISION_TYPE,
    #         decision_tracker.MODEL_KEY: self.dummy_model_name,
    #         decision_tracker.ITEM_KEY: variants[0],
    #         decision_tracker.ITEMS_COUNT_KEY: len(variants),
    #     }
    #
    #     expected_request_json = json.dumps(expected_track_body, sort_keys=False)
    #
    #     def custom_matcher(request):
    #         request_dict = deepcopy(request.json())
    #         del request_dict[decision_tracker.MESSAGE_ID_KEY]
    #
    #         if json.dumps(request_dict, sort_keys=False) != \
    #                 expected_request_json:
    #
    #             print('request body:')
    #             print(request.text)
    #             print('expected body:')
    #             print(expected_request_json)
    #             return None
    #         return True
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    # def test_track_invalid_model_name(self):
    #
    #     with catch_warnings(record=True) as w:
    #         simplefilter("always")
    #         model_name = ''
    #         decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #         result = decision_tracker.track(ranked_variants=[1, 2, 3], givens=None, model_name=model_name)
    #         assert len(w) > 0
    #         assert result is None
    #
    #     with catch_warnings(record=True) as w:
    #         simplefilter("always")
    #         model_name = '!@#$%^&*()'
    #         decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #         result = decision_tracker.track(ranked_variants=[1, 2, 3], givens=None, model_name=model_name)
    #         assert len(w) > 0
    #         assert result is None
    #
    #     with catch_warnings(record=True) as w:
    #         simplefilter("always")
    #         model_name = ''.join(['a' for _ in range(65)])
    #         decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #         result = decision_tracker.track(ranked_variants=[1, 2, 3], givens=None, model_name=model_name)
    #         assert len(w) > 0
    #         assert result is None
    #
    # def test_add_float_reward(self):
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     variants = [el for el in range(0, 1)]
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    #     reward = 1.0
    #
    #     expected_add_reward_body = {
    #         decision_tracker.TYPE_KEY: decision_tracker.REWARD_TYPE,
    #         decision_tracker.MODEL_KEY: self.dummy_model_name,
    #         decision_tracker.REWARD_KEY: reward,
    #         decision_tracker.REWARD_ID_KEY: decision_id,
    #     }
    #
    #     expected_request_json = json.dumps(expected_add_reward_body, sort_keys=False)
    #
    #     def custom_matcher(request):
    #         request_dict = deepcopy(request.json())
    #         del request_dict[decision_tracker.MESSAGE_ID_KEY]
    #
    #         if json.dumps(request_dict, sort_keys=False) != \
    #                 expected_request_json:
    #
    #             print('raw request body:')
    #             print(request.text)
    #             print('compared request string')
    #             print(json.dumps(request_dict, sort_keys=False))
    #             print('expected body:')
    #             print(expected_request_json)
    #             return None
    #         return True
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    # def test_add_int_reward(self):
    #
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     variants = [el for el in range(0, 1)]
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    #     reward = 1
    #
    #     expected_add_reward_body = {
    #         decision_tracker.TYPE_KEY: decision_tracker.REWARD_TYPE,
    #         decision_tracker.MODEL_KEY: self.dummy_model_name,
    #         decision_tracker.REWARD_KEY: reward,
    #         decision_tracker.REWARD_ID_KEY: decision_id,
    #     }
    #
    #     expected_request_json = json.dumps(expected_add_reward_body, sort_keys=False)
    #
    #     def custom_matcher(request):
    #         request_dict = deepcopy(request.json())
    #         del request_dict[decision_tracker.MESSAGE_ID_KEY]
    #
    #         if json.dumps(request_dict, sort_keys=False) != \
    #                 expected_request_json:
    #
    #             print('raw request body:')
    #             print(request.text)
    #             print('compared request string')
    #             print(json.dumps(request_dict, sort_keys=False))
    #             print('expected body:')
    #             print(expected_request_json)
    #             return None
    #         return True
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             print('### decision_id ###')
    #             print(f'Decision ID: {decision_id is None}')
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    # def test_add_reward_bad_reward_type(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     decision_id_container = {'decision_id': None}
    #
    #     def custom_matcher_caching_decision_id(request):
    #         request_dict = deepcopy(request.json())
    #         decision_id_container['decision_id'] = \
    #             request_dict[decision_tracker.MESSAGE_ID_KEY]
    #         return True
    #
    #     variants = [el for el in range(0, 1)]
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher_caching_decision_id)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    #     decision_id = decision_id_container['decision_id']
    #     reward = 'bad_reward'
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with raises(AssertionError) as aerr:
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #
    # def test_add_reward_inf(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     decision_id_container = {'decision_id': None}
    #
    #     def custom_matcher_caching_decision_id(request):
    #         request_dict = deepcopy(request.json())
    #         decision_id_container['decision_id'] = \
    #             request_dict[decision_tracker.MESSAGE_ID_KEY]
    #         return True
    #
    #     variants = [el for el in range(0, 1)]
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher_caching_decision_id)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    #     decision_id = decision_id_container['decision_id']
    #
    #     reward = math.inf
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with raises(AssertionError) as aerr:
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #
    #     reward = -math.inf
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with raises(AssertionError) as aerr:
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #
    # def test_add_reward_none(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     decision_id_container = {'decision_id': None}
    #
    #     def custom_matcher_caching_decision_id(request):
    #         request_dict = deepcopy(request.json())
    #         decision_id_container['decision_id'] = \
    #             request_dict[decision_tracker.MESSAGE_ID_KEY]
    #         return True
    #
    #     variants = [el for el in range(0, 1)]
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success',
    #                additional_matcher=custom_matcher_caching_decision_id)
    #
    #         with catch_warnings(record=True) as w:
    #             simplefilter("always")
    #             np.random.seed(self.sample_seed)
    #             decision_id = decision_tracker.track(
    #                 ranked_variants=variants,
    #                 givens=None, model_name=self.dummy_model_name)
    #             time.sleep(0.175)
    #             assert len(w) == 0
    #
    #         assert is_valid_ksuid(decision_id)
    #
    #     decision_id = decision_id_container['decision_id']
    #
    #     reward = None
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with raises(AssertionError) as aerr:
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #
    #     reward = np.nan
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #
    #         with raises(AssertionError) as aerr:
    #             decision_tracker.add_reward(
    #                 reward=reward, model_name=self.dummy_model_name, reward_id=decision_id)
    #             assert aerr
    #
    # def test_add_reward_raises_for_none_model_name(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #     with raises(AssertionError) as aerr:
    #         decision_tracker.add_reward(reward=1.0, model_name=None, reward_id=str(Ksuid()))
    #
    # def test_add_reward_raises_for_invalid_model_name(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #     with raises(AssertionError) as aerr:
    #         model_name = ''
    #         decision_tracker.add_reward(reward=1.0, model_name=model_name, reward_id=str(Ksuid()))
    #
    #     with raises(AssertionError) as aerr:
    #         model_name = '!@#$%^&*()'
    #         decision_tracker.add_reward(reward=1.0, model_name=model_name, reward_id=str(Ksuid()))
    #
    #     with raises(AssertionError) as aerr:
    #         model_name = ''.join(['a' for _ in range(65)])
    #         decision_tracker.add_reward(reward=1.0, model_name=model_name, reward_id=str(Ksuid()))
    #
    # def test_trck_url_setter_raises_for_none(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     with raises(AssertionError) as aerr:
    #         decision_tracker.track_url = None
    #
    # def test_tracker_with_api_headers(self):
    #     # self, track_url: str, max_runners_up: int = 50, track_api_key: str = None
    #     dummy_api_key = 'dummy-api-key'
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url, track_api_key=dummy_api_key)
    #     decision_tracker.max_runners_up = self.max_runners_up
    #
    #     headers_cache = {'headers': None}
    #
    #     def cache_headers(request):
    #         print('CACHE HEADERS')
    #         headers_cache['headers'] = request._request.headers
    #         return True
    #
    #     mockup_body = {"k1": 1, "k2": 2}
    #     expected_headers = {
    #         'Content-Type': 'application/json',
    #         decision_tracker.API_KEY_HEADER: dummy_api_key}
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success', additional_matcher=cache_headers)
    #
    #         decision_id = decision_tracker.post_improve_request(body_values=mockup_body)
    #         time.sleep(0.175)
    #
    #         assert is_valid_ksuid(decision_id)
    #
    #         for k, v in expected_headers.items():
    #             assert k in headers_cache['headers']
    #             assert v == headers_cache['headers'][k]
    #
    # def test_track_returns_none_for_model_name_none(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #         # ranked_variants: list or np.ndarray, givens: dict, model_name: str
    #         decision_id = decision_tracker.track(ranked_variants=[0, 1, 2], givens={}, model_name=None)
    #         assert decision_id is None
    #         time.sleep(0.175)
    #
    # def test_track_returns_none_for_bad_model_name(self):
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     bad_model_name = '!@#$%^&*()'
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, text='success')
    #         # ranked_variants: list or np.ndarray, givens: dict, model_name: str
    #         decision_id = decision_tracker.track(ranked_variants=[0, 1, 2], givens={}, model_name=bad_model_name)
    #         assert decision_id is None
    #         time.sleep(0.175)
    #
    # def test_post_improve_request_does_not_block_io(self):
    #     # make multiple requests and check that:
    #     # max N threads are running
    #     # I/O is not blocked
    #     decision_tracker = rtr.RewardTracker(track_url=self.track_url)
    #     dummy_body = {
    #         'type': 'decision',
    #         'model': 'test-model-0',
    #         'variant': 'asd',
    #         'count': 1}
    #
    #     requests_attempts = 500
    #
    #     msg_ids = [None] * requests_attempts
    #     executor_threads = [None] * requests_attempts
    #
    #     with rqm.Mocker() as m:
    #         m.post(self.track_url, status_code=200)
    #         for request_index in range(requests_attempts):
    #             msg_ids[request_index] = decision_tracker.post_improve_request(body_values=dummy_body)
    #             # assert that each time at most <= MAX_TRACK_THREADS tasks are in queue
    #             executor_threads[request_index] = len(improveai.track_improve_executor._threads)
    #
    #         # wait for all threads to finish
    #         time.sleep(3)
    #     # assert that all threads finished
    #     current_qsize = improveai.track_improve_executor._work_queue.qsize()
    #     print('### current_qsize ###')
    #     assert improveai.track_improve_executor._work_queue.qsize() == 0
    #
    #     assert all([el is not None for el in msg_ids])
    #     assert all([el is not None for el in executor_threads])
    #
    #     assert max(executor_threads) <= MAX_TRACK_THREADS
    #
    #     assert 1 < np.mean(executor_threads) <= MAX_TRACK_THREADS

    # # TODO test track_with_sample()