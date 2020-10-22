import json
import numpy as np

from choosers.basic_choosers import BasicChooser
from choosers.mlmodel_chooser import BasicMLModelChooser
from choosers.xgb_chooser import BasicNativeXGBChooser
from utils.gen_purp_utils import constant


class DecisionModel:

    @property
    def chooser(self) -> BasicChooser:
        return self._chooser

    @chooser.setter
    def chooser(self, new_val: BasicChooser):
        self._chooser = new_val

    @property
    def model_kind(self) -> str:
        return self._model_kind

    @model_kind.setter
    def model_kind(self, new_val: str):
        self._model_kind = new_val

    @property
    def pth_to_model(self) -> str:
        return self._pth_to_model

    @pth_to_model.setter
    def pth_to_model(self, new_val: str):
        self._pth_to_model = new_val

    @constant
    def SUPPORTED_MODEL_KINDS():
        return ['mlmodel', 'xgb_native']

    @constant
    def SUPPORTED_CALLS():
        return ['score', 'sort', 'choose']

    def __init__(self, model_kind: str, model_pth: str):
        self.chooser = None
        self.model_kind = model_kind
        self.pth_to_model = model_pth
        self._set_chooser()
        self._load_choosers_model()

    def _set_chooser(self):
        """
        Sets desired chooser

        Returns
        -------
        None

        """

        if self.model_kind == 'mlmodel':
            self.chooser = BasicMLModelChooser()
        elif self.model_kind == 'xgb_native':
            self.chooser = BasicNativeXGBChooser()

    def _load_choosers_model(self):
        """
        Loads desired model using chooser API call (load_model method)

        Returns
        -------
        None

        """
        self.chooser.load_model(pth_to_model=self.pth_to_model)

    def _get_json_frm_str(self, json_str) -> list or dict or None:
        """
        Attempts to convert input json string into json

        Parameters
        ----------
        json_str: str
            JSON string to be converted into list or dict

        Returns
        -------
        list or dict or None
            JSON laoded from string or None if loading fails

        """
        try:
            loaded_json = json.loads(json_str)
        except Exception as exc:
            print(
                'Failed to load json from provided JSON string: \n {}'
                .format(json_str))
            loaded_json = None
        return loaded_json

    def _check_if_single_variant(self, variants_json) -> bool:
        """
        Determines if provided variant(s) JSON is a single variant or list of
        variants

        Parameters
        ----------
        variants_json: list or dict
            either single variant as dict or multiple variants as list of dicts

        Returns
        -------
        bool
            True if input json is a single variant False if multiple variants
            were provided

        """
        if isinstance(variants_json, list):
            return False
        elif isinstance(variants_json, dict):
            return True
        else:
            raise TypeError('Unsupported type of provided variants_json!')

    def _get_as_is_or_json_str(
            self, input_val: object, cli_call: bool) -> object:
        """
        If cli_call is True atempts to return json otherwise returns original
        input

        Parameters
        ----------
        input_val: object
            value to be returned or serialized to JSON
        cli_call: bool
            if True attempts JSON serialization of input

        Returns
        -------
        object
            plain input or JSON string

        """
        if not cli_call:
            return input_val
        else:
            dumped_val = input_val
            if isinstance(dumped_val, np.ndarray):
                dumped_val = input_val.tolist()

            return json.dumps(dumped_val)

    def score(
            self, variants: str, context: str, model_metadata: str = '',
            cli_call: bool = False, sigmoid_correction: bool = True,
            sigmoid_const: float = 0.5, return_plain_scores: bool = False,
            plain_scores_idx: int = 1, **kwargs) -> np.ndarray or str:
        """
        Scores provided variants with provided context

        Parameters
        ----------
        variants: list or dict
            variant(s) to score
        context: dict
            dict with lookup table
        sigmoid_correction: bool
            should results be corrected with sigmoid
        return_plain_scores: bool
            should plain floats be returned or tuples of
            (variant, score, class)
        plain_scores_idx: int
            index of 'column' containing plain float scores - maybe should be
             refactored

        Returns
        -------
        np.ndarray or str
            np.ndarray if this is not cli call else results as json string

        """
        variants_json = self._get_json_frm_str(json_str=variants)
        context_json = self._get_json_frm_str(json_str=context)
        model_metadata_json = self._get_json_frm_str(json_str=model_metadata)

        score_kwgs = {
            'sigmoid_correction': sigmoid_correction,
            'sigmoid_const': sigmoid_const}

        is_single_variant = \
            self._check_if_single_variant(variants_json=variants_json)
        if is_single_variant:
            variants_w_scores = \
                self.chooser.score(
                    variant=variants_json, context=context_json,
                    model_metadata=model_metadata_json, **score_kwgs)
        else:
            variants_w_scores = \
                self.chooser.score_all(
                    variants=variants_json, context=context_json,
                    model_metadata=model_metadata_json, **score_kwgs)

        # ret_variants_w_scores = variants_w_scores
        # if isinstance(variants_w_scores, float):
        #     ret_variants_w_scores = \
        #         np.array([[variants_json, variants_w_scores]]).reshape((1, 2))

        if return_plain_scores:
            return variants_w_scores[:, plain_scores_idx]

        return self._get_as_is_or_json_str(
            input_val=variants_w_scores, cli_call=cli_call)

    def sort(
            self, variants: str, context: str, model_metadata: str,
            cli_call: bool = False, sigmoid_correction: bool = True,
            sigmoid_const: float = 0.5, **kwargs) -> np.ndarray or str:
        """
        Scores and sorts provided variants and context

        Parameters
        ----------
        variants: str
            json string with single variant or list of variants
        context: str
            json string with lookup table
        cli_call: bool
            is this exact cli_call or from inside code call

        Returns
        -------
        np.ndarray or str
            array with results or json string

        """

        variants_w_scores = \
            self.score(
                variants=variants, context=context,
                model_metadata=model_metadata, cli_call=False,
                sigmoid_correction=sigmoid_correction,
                sigmoid_const=sigmoid_const)
        srtd_variants_w_scores = \
            self.chooser.sort(variants_w_scores=variants_w_scores)

        return self._get_as_is_or_json_str(
            input_val=srtd_variants_w_scores, cli_call=cli_call)

    def choose(
            self, variants: str, context: str, model_metadata: str,
            cli_call: bool = False, sigmoid_correction: bool = True,
            sigmoid_const: float = 0.5, **kwargs):

        variants_w_scores = \
            self.score(
                variants=variants, context=context,
                model_metadata=model_metadata, cli_call=False,
                sigmoid_correction=sigmoid_correction,
                sigmoid_const=sigmoid_const)
        chosen_variant = \
            self.chooser.choose(variants_w_scores=variants_w_scores)

        return self._get_as_is_or_json_str(
            input_val=chosen_variant, cli_call=cli_call)
