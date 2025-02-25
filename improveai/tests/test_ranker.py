import numpy as np
import os
from pytest import raises, fixture
import re

from improveai.chooser import XGBChooser
from improveai.ranker import Ranker
from improveai.scorer import Scorer


class TestRanker:

    @property
    def model_url(self):
        return self._model_url

    @model_url.setter
    def model_url(self, value):
        assert value is not None
        self._model_url = value

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @fixture(autouse=True)
    def prep_env(self):
        self.model_url = os.getenv('DUMMY_MODEL_PATH', None)
        self.context = {'ga': 1, 'gb': 0}

    def test_constructor_prefers_scorer_over_model_url(self):

        scorer = Scorer(model_url=self.model_url)
        ranker = Ranker(scorer=scorer)

        assert isinstance(ranker.scorer, Scorer)

        assert ranker.model_url == scorer.model_url

    def test_constructor_with_model_url(self):
        ranker = Ranker(model_url=self.model_url)
        assert isinstance(ranker.scorer, Scorer)
        assert isinstance(ranker.scorer.chooser, XGBChooser)
        assert ranker.model_url == self.model_url

    def test_constructor_with_gzipped_model(self):
        ranker = Ranker(model_url=self.model_url + '.gz')
        assert isinstance(ranker.scorer, Scorer)
        assert isinstance(ranker.scorer.chooser, XGBChooser)
        assert ranker.model_url == self.model_url + '.gz'

    def test_constructor_with_gzipped_model_relative_path(self):
        user_path_chunk = os.path.expanduser('~')
        # make sure to replace front chunk of path
        relative_gzipped_model_url = \
            re.sub("^" + user_path_chunk, '~', self.model_url)
        ranker = Ranker(model_url=relative_gzipped_model_url + '.gz')
        assert isinstance(ranker.scorer, Scorer)
        assert isinstance(ranker.scorer.chooser, XGBChooser)
        assert ranker.model_url == relative_gzipped_model_url + '.gz'

    def test_constructor_raises_for_bad_scorer_type(self):
        with raises(AssertionError) as aerr:
            Ranker(scorer=123)

        with raises(AssertionError) as aerr:
            Ranker(scorer='abc')

        with raises(AssertionError) as aerr:
            Ranker(scorer=[1, 2, 3])

    def test_rank_no_context(self):
        ranker = Ranker(model_url=self.model_url)
        items = ['b', 'a', 'd']
        np.random.seed(0)
        ranked_items = ranker.rank(items=items, context=None)
        expected_ranked_items = ['b', 'a', 'd']
        np.testing.assert_array_equal(ranked_items, expected_ranked_items)

    def test_rank(self):
        ranker = Ranker(model_url=self.model_url)
        items = ['c', 'a', 'd']
        np.random.seed(0)
        ranked_items = ranker.rank(items=items, context=self.context)
        expected_ranked_items = ['a', 'c', 'd']
        np.testing.assert_array_equal(ranked_items, expected_ranked_items)

    def test_rank_tuple(self):
        ranker = Ranker(model_url=self.model_url)
        items = tuple(['c', 'a', 'd'])
        np.random.seed(0)
        ranked_items = ranker.rank(items=items, context=self.context)
        expected_ranked_items = tuple(['a', 'c', 'd'])
        np.testing.assert_array_equal(ranked_items, expected_ranked_items)

    def test_rank_ndarray(self):
        ranker = Ranker(model_url=self.model_url)
        items = np.array(['c', 'a', 'd'])
        np.random.seed(0)
        ranked_items = ranker.rank(items=items, context=self.context)
        expected_ranked_items = np.array(['a', 'c', 'd'])
        np.testing.assert_array_equal(ranked_items, expected_ranked_items)

    def test_rank_returns_same_items(self):
        scorer = Scorer(model_url=self.model_url)
        ranker = Ranker(model_url=self.model_url)

        items = np.array(['c', 'a', 'd'])

        np.random.seed(0)
        scores = scorer.score(items=items, context=self.context)
        items_sorted_by_scores = np.array(items)[np.argsort(scores)[::-1]]

        np.random.seed(0)
        ranked_items = ranker.rank(items=items, context=self.context)
        assert all([items_sorted_by_scores[i] == ranked_items[i] for i in range(len(items))])

    def test_rank_returns_descending_order(self):
        scorer = Scorer(model_url=self.model_url)
        ranker = Ranker(scorer=scorer)

        items = ['c', 'a', 'd']

        np.random.seed(0)
        # calculate scores
        scores = scorer.score(items=items, context=self.context)
        items_sorted_by_scores = np.array(items)[np.argsort(scores)[::-1]]
        np.random.seed(0)
        # calculate ranked items
        ranked_items = ranker.rank(items=items, context=self.context)

        np.testing.assert_array_equal(ranked_items, items_sorted_by_scores)

    def test_rank_raises_for_empty_items(self):
        ranker = Ranker(model_url=self.model_url)

        with raises(AssertionError) as aerr:
            ranker.rank(items=[], context=None)

        with raises(AssertionError) as aerr:
            ranker.rank(items=tuple(), context=None)

        with raises(AssertionError) as aerr:
            ranker.rank(items=np.array([]), context=None)

    def test_rank_raises_for_non_json_encodable_items(self):
        ranker = Ranker(model_url=self.model_url)
        items = [np.array([1, 2, 3]) for _ in range(10)]
        with raises(ValueError) as verr:
            ranker.rank(items=items, context=None)

    def test_rank_raises_for_non_json_encodable_context(self):
        ranker = Ranker(model_url=self.model_url)
        items = [1, 2, 3]
        context = np.array([1, 2, 3])
        with raises(ValueError) as verr:
            ranker.rank(items=items, context=context)

    def test_attempt_to_set_model_url_raises(self):
        ranker = Ranker(model_url=self.model_url)
        with raises(AttributeError) as aerr:
            ranker.model_url = 'abc'

    def test_attempt_to_set_scorer_raises(self):
        ranker = Ranker(model_url=self.model_url)
        with raises(AttributeError) as aerr:
            ranker.scorer = 'abc'

    def test_ranker_constructor_raises_for_scorer_none_and_model_url_none(self):
        with raises(ValueError) as verr:
            Ranker(scorer=None, model_url=None)
