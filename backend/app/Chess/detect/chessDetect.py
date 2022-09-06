# Integrated from https://github.com/georg-wolflein/chesscog

import numpy as np
import chess
from pathlib import Path
import torch
from PIL import Image
import functools
import typing
from recap import URI, CfgNode as CN

from .chesscog.corner_detection import find_corners, resize_image
from .chesscog.occupancy_classifier import create_dataset as create_occupancy_dataset
from .chesscog.piece_classifier import create_dataset as create_piece_dataset
from .chesscog.core import device, DEVICE
from .chesscog.core.dataset import build_transforms, Datasets
from .chesscog.core.dataset import name_to_piece

class ChessRecognizer:
    """A class implementing the entire chess inference pipeline.

    Once you create an instance of this class, the CNNs are loaded into memory (possibly the GPU if available), so if you want to perform multiple inferences, they should all use one instance of this class for performance purposes.
    """

    _squares = list(chess.SQUARES)

    def __init__(self, classifiers_folder: Path = URI("models://")):
        """Constructor.

        Args:
            classifiers_folder (Path, optional): the path to the classifiers (supplying a different path is especially useful because the transfer learning classifiers are located at ``models://transfer_learning``). Defaults to ``models://``.
        """
        self._corner_detection_cfg = CN.load_yaml_with_base(
            "config://corner_detection.yaml")

        self._occupancy_cfg, self._occupancy_model = self._load_classifier(
            classifiers_folder / "occupancy_classifier")
        self._occupancy_transforms = build_transforms(
            self._occupancy_cfg, mode=Datasets.TEST)
        self._pieces_cfg, self._pieces_model = self._load_classifier(
            classifiers_folder / "piece_classifier")
        self._pieces_transforms = build_transforms(
            self._pieces_cfg, mode=Datasets.TEST)
        self._piece_classes = np.array(list(map(name_to_piece,
                                                self._pieces_cfg.DATASET.CLASSES)))

    @classmethod
    def _load_classifier(cls, path: Path):
        model_file = next(iter(path.glob("*.pt")))
        yaml_file = next(iter(path.glob("*.yaml")))
        cfg = CN.load_yaml_with_base(yaml_file)
        model = torch.load(model_file, map_location=DEVICE)
        model = device(model)
        model.eval()
        return cfg, model

    def _classify_occupancy(self, img: np.ndarray, turn: chess.Color, corners: np.ndarray) -> np.ndarray:
        warped = create_occupancy_dataset.warp_chessboard_image(
            img, corners)
        square_imgs = map(functools.partial(
            create_occupancy_dataset.crop_square, warped, turn=turn), self._squares)
        square_imgs = map(Image.fromarray, square_imgs)
        square_imgs = map(self._occupancy_transforms, square_imgs)
        square_imgs = list(square_imgs)
        square_imgs = torch.stack(square_imgs)
        square_imgs = device(square_imgs)
        occupancy = self._occupancy_model(square_imgs)
        occupancy = occupancy.argmax(
            axis=-1) == self._occupancy_cfg.DATASET.CLASSES.index("occupied")
        occupancy = occupancy.cpu().numpy()
        return occupancy

    def _classify_pieces(self, img: np.ndarray, turn: chess.Color, corners: np.ndarray, occupancy: np.ndarray) -> np.ndarray:
        occupied_squares = np.array(self._squares)[occupancy]
        warped = create_piece_dataset.warp_chessboard_image(
            img, corners)
        piece_imgs = map(functools.partial(
            create_piece_dataset.crop_square, warped, turn=turn), occupied_squares)
        piece_imgs = map(Image.fromarray, piece_imgs)
        piece_imgs = map(self._pieces_transforms, piece_imgs)
        piece_imgs = list(piece_imgs)
        piece_imgs = torch.stack(piece_imgs)
        piece_imgs = device(piece_imgs)
        pieces = self._pieces_model(piece_imgs)
        pieces = pieces.argmax(axis=-1).cpu().numpy()
        pieces = self._piece_classes[pieces]
        all_pieces = np.full(len(self._squares), None, dtype=np.object)
        all_pieces[occupancy] = pieces
        return all_pieces

    def predict(self, img: np.ndarray, turn: chess.Color = chess.WHITE) -> typing.Tuple[chess.Board, np.ndarray]:
        """Perform an inference.

        Args:
            img (np.ndarray): the input image (RGB)
            turn (chess.Color, optional): the current player. Defaults to chess.WHITE.

        Returns:
            typing.Tuple[chess.Board, np.ndarray]: the predicted position on the board and the four corner points
        """
        with torch.no_grad():
            img, img_scale = resize_image(self._corner_detection_cfg, img)
            corners = find_corners(self._corner_detection_cfg, img)
            occupancy = self._classify_occupancy(img, turn, corners)
            pieces = self._classify_pieces(img, turn, corners, occupancy)

            board = chess.Board()
            board.clear_board()
            for square, piece in zip(self._squares, pieces):
                if piece:
                    board.set_piece_at(square, piece)
            corners = corners / img_scale
            return board, corners


class TimedChessRecognizer(ChessRecognizer):
    """A subclass of :class:`ChessRecognizer` that additionally records the time taken for each step of the pipeline during inference.
    """

    def predict(self, img: np.ndarray, turn: chess.Color = chess.WHITE) -> typing.Tuple[chess.Board, np.ndarray, dict]:
        """Perform an inference.

        Args:
            img (np.ndarray): the input image (RGB)
            turn (chess.Color, optional): the current player. Defaults to chess.WHITE.

        Returns:
            typing.Tuple[chess.Board, np.ndarray, dict]: the predicted position on the board, the four corner points, and a dict containing the time taken for each stage of the inference pipeline
        """

        from timeit import default_timer as timer
        with torch.no_grad():
            t1 = timer()
            img, img_scale = resize_image(self._corner_detection_cfg, img)
            corners = find_corners(self._corner_detection_cfg, img)
            t2 = timer()
            occupancy = self._classify_occupancy(img, turn, corners)
            t3 = timer()
            pieces = self._classify_pieces(img, turn, corners, occupancy)
            t4 = timer()

            board = chess.Board()
            board.clear()
            board.turn = turn
            for square, piece in zip(self._squares, pieces):
                if piece:
                    board.set_piece_at(square, piece)
            corners = corners / img_scale
            t5 = timer()

            times = {
                "corner_detection": t2-t1,
                "occupancy_classification": t3-t2,
                "piece_classification": t4-t3,
                "prepare_results": t5-t4
            }

            return board, corners, times

recognizer = ChessRecognizer()