from AnalysisCommonTools import AnalysisCommonTools
from graphers.MatplotlibFigureCreator import MatplotlibFigureCreator
from machine_learning.ModelManager import ModelManager
from machine_learning.model_preprocessors.DataWindowManager import DataWindowManager
from machine_learning.model_preprocessors.SklearnStandardScaler import SklearnStandardScaler
from machine_learning.models.KerasLSTMModel import KerasLSTMModel
from machine_learning.models.SklearnElasticNetModel import SklearnElasticNetModel
from machine_learning.models.SklearnLinearRegressionModel import SklearnLinearRegressionModel
from model.PredictorResult import PredictorResult
from model.Table import Table
from model.ocean_devices.WaveGliderV2 import WaveGliderV2
from model.params.BasicPlotParams import BasicPlotParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.MarkerParams import MarkerParams
from model.params.compound_params.PlotStylishParams import PlotStylishParams
from storer.CsvPandasStorer import CsvPandasStorer
from storer.MatplotlibFigureStorer import MatplotlibFigureStorer

DATA_DIR = "./data"
RESULT_DIR = "./results/predictive"
common_analysis_tools = AnalysisCommonTools(DATA_DIR, RESULT_DIR)

def main():
    (ocean_21, weather_21, glider_21,
     ocean_22, weather_22, glider_22, drifted_22, glider_drifted_22, weather_drifted_22, seabed_23) = common_analysis_tools.get_data()
    results_1, results_2 = not_splited_glider(glider_21, glider_22, glider_drifted_22,
                                              ModelManager(SklearnStandardScaler(),
                                                           {
                                                               "Elastic Net": SklearnElasticNetModel(alpha=0.00001),
                                                               "Regresión lineal": SklearnLinearRegressionModel(),
                                                               "LSTM": KerasLSTMModel(input_dim=3, output_dim=1,
                                                                                      epochs=1500,
                                                                                      learning_rate=0.0001,
                                                                                      hidden_size=16, lstm_units=4,
                                                                                      batch_size=32)
                                                           }),
                                              ("Entrenado con datos de 2022 predicen datos de la desviación",
                                               "Entrenado con datos de 2022 predicen datos de 2021"),
                                              ("/normal_22.png", "/normal_21.png"),
                                              (
                                              "Entrenados con datos de \n la misión de 2022 predicen datos del desvío.",
                                              "Entrenados con datos de \n la misión de 2022 predicen datos de \n la misión de 2021.")
                                              )

    results_3, results_4 = windowed_glider(glider_21, glider_22, glider_drifted_22,
                                           ModelManager(SklearnStandardScaler(),
                                                        {
                                                            "Elastic Net": SklearnElasticNetModel(alpha=0.015),
                                                            "Regresión lineal": SklearnLinearRegressionModel(),
                                                            "LSTM": KerasLSTMModel(72,24, 100, 0.005,
                                                                                   16, 2,
                                                                                   8),
                                                        }),
                                           ("Entrenado con ventanas de datos de 2022 predicen datos de la desviación",
                                            "Entrenado con ventanas de datos de 2022 predicen datos de 2021"),
                                           ("/resultados_modelo_ventanas_22.png",
                                            "/resultados_modelo_ventanas_21.png"),
                                           (
                                           "Modelos con ventanas entrenados con \n datos de la misión de 2022 \n predicen datos de la misión de 2022",
                                           "Modelos con ventanas entrenados con \n datos de la misión de 2022 \n predicen datos de la misión de 2021"), )
    results_5, results_6 = splited_glider(glider_21, glider_22, ModelManager(SklearnStandardScaler(),
                                                                             {
                                                                                 "Elastic Net": SklearnElasticNetModel(
                                                                                     alpha=0.05),
                                                                                 "Regresión lineal": SklearnLinearRegressionModel(),
                                                                                 "LSTM": KerasLSTMModel(3,
                                                                                                        1,
                                                                                                        400,
                                                                                                        0.001,
                                                                                                        64,
                                                                                                        12,
                                                                                                        16)}),
                                          ("Entrenado con el 66% datos de 2021 predicen datos del 33% restante",
                                           "Entrenado con el 66% de datos de 2021 predicen datos de 2022"),
                                          ("/split_21.png",
                                           "/split_22.png"),
                                          (
                                          "Modelos sin ventanas entrenados con el 66% \ndatos de  la misión de 2021 \npredice el 33% restante",
                                          "Modelos sin ventanas entrenados con el 66% \ndatos de  la misión de 2021 \npredice datos de la misión de 2022"))
    results_7, results_8 = windowed_splited_glider(glider_21, glider_22, ModelManager(SklearnStandardScaler(),
                                                                                      {
                                                                                          "Elastic Net": SklearnElasticNetModel(
                                                                                              alpha=0.015),
                                                                                          "Regresión lineal": SklearnLinearRegressionModel(),
                                                                                          "LSTM": KerasLSTMModel(72,
                                                                                                                 24,
                                                                                                                 1000,
                                                                                                                 0.0005,
                                                                                                                 128,
                                                                                                                 32,
                                                                                                                 8),
                                                                                      }),
                                                   (
                                                   "Entrenado con ventanas del 66% datos de 2021 predicen datos del 33% restante",
                                                   "Entrenado con ventanas del 66% de datos de 2021 predicen datos de 2022"),
                                                   ("/resultados_modelo_con_ventanas_21_split_21.png",
                                                    "/resultados_modelo_con_ventanas_21_split_22.png"),
                                                   (
                                                       "Modelos con ventanas entrenados con el 66% \ndatos de la misión de 2021 predicen \nel 33% restante",
                                                       "Modelos con ventanas entrenados con el 66% \ndatos de la misión de 2021 predicen \ndatos de la misión de 2022"))

    CsvPandasStorer().store(
        merge_tables(
            results_1, results_2,
            results_3, results_4,
            results_5, results_6,
            results_7, results_8
        ),
        RESULT_DIR + "/errores.csv", "", True)


def merge_tables(*results: Table) -> Table:
    final_table = Table([], [])
    for table in results:
        final_table_column_labels = list(map(lambda final_table_col: final_table_col.label, final_table.columns))
        for column in table.columns:
            if column.label not in final_table_column_labels:
                final_table.columns.append(column)
            else:
                for final_table_column in final_table.columns:
                    if column.label == final_table_column.label:
                        final_table_column.values.extend(column.values)
        final_table.indexes.extend(table.indexes)
    return final_table


def splited_glider(glider_to_train: WaveGliderV2, glider_to_predict: WaveGliderV2,
                   model_manager: ModelManager,
                   predictions_names: tuple[str, str], png_filenames: tuple[str, str],
                   titles: tuple[str, str]):
    train_percent = 0.8
    train_idx = round(len(glider_to_train.ocean.temperature_c) * train_percent)
    model_manager.train(
        create_x_input(glider_to_train)[:train_idx],
        glider_to_train.ocean.temperature_c[:train_idx])
    return (predict_with_split(glider_to_train, model_manager, predictions_names[0], titles[0], png_filenames[0],
                               train_percent)), (
        predict(glider_to_predict, model_manager, predictions_names[1], titles[1], png_filenames[1]))


def windowed_splited_glider(glider_to_train: WaveGliderV2, glider_to_predict: WaveGliderV2,
                            model_manager: ModelManager,
                            predictions_names: tuple[str, str], png_filenames: tuple[str, str],
                            titles: tuple[str, str]):
    train_percent = 0.8
    window_size = 24
    data_window_manager = DataWindowManager()
    x_train = create_x_input(glider_to_train)
    x_train, y_train = data_window_manager.generate_window(window_size, x_train[
                                                                        :round(
                                                                            len(glider_to_train.weather.temperature_c) * train_percent)],
                                                           glider_to_train.ocean.temperature_c[
                                                           :round(
                                                               len(glider_to_train.weather.temperature_c) * train_percent)])

    model_manager.train(x_train[:-1], y_train[1:])
    return (
        predict_windowed_splitted(glider_to_train, model_manager, predictions_names[0], titles[0], png_filenames[0],
                                  data_window_manager, window_size, train_percent)), (
        predict_windowed(glider_to_predict, model_manager, predictions_names[1], titles[1], png_filenames[1],
                         data_window_manager, window_size))


def not_splited_glider(glider_to_predict: WaveGliderV2, glider_to_train: WaveGliderV2,
                       glider_drifted_22: WaveGliderV2, model_manager: ModelManager,
                       predictions_names: tuple[str, str], png_filenames: tuple[str, str],
                       titles: tuple[str, str]):
    train_x = create_x_input(glider_to_train)
    model_manager.train(train_x, glider_to_train.ocean.temperature_c)
    return (predict(glider_drifted_22, model_manager, predictions_names[0], titles[0], png_filenames[0])), (
        predict(glider_to_predict, model_manager, predictions_names[1], titles[1], png_filenames[1]))


def create_x_input(glider: WaveGliderV2):
    return [[glider.weather.temperature_c[i], glider.weather.wind_speed_kt[i],
             glider.weather.wind_gust_speed_kt[i]]
            for i in range(len(glider.weather.temperature_c))]


def predict(glider_to_predict: WaveGliderV2, model_manager: ModelManager, prediction_name: str, title: str,
            png_filename: str) -> Table:
    results = model_manager.predict(create_x_input(glider_to_predict),
                                    glider_to_predict.ocean.temperature_c)
    graph_model_results(results, title, [glider_to_predict.ocean.timestamp]  * len(model_manager.models),
                        png_filename)
    return get_table_results(results, prediction_name)


def predict_with_split(glider_to_predict: WaveGliderV2, model_manager: ModelManager, prediction_name: str, title: str,
                       png_filename: str, train_percent: float):
    test_idx = round(len(glider_to_predict.weather.temperature_c) * train_percent)
    test_x = create_x_input(glider_to_predict)
    results = model_manager.predict(test_x[test_idx:],
                                    glider_to_predict.ocean.temperature_c[test_idx:])
    ticks = [glider_to_predict.ocean.timestamp[test_idx:]] * len(model_manager.models)
    graph_model_results(results, title, ticks,
                        png_filename)
    return get_table_results(results, prediction_name)


def windowed_glider(glider_to_predict: WaveGliderV2, glider_to_train: WaveGliderV2,
                    glider_drifted_22: WaveGliderV2, model_manager: ModelManager,
                    prediction_names: tuple[str, str], png_filenames: tuple[str, str],
                    titles: tuple[str, str]
                    ):
    data_window_manager = DataWindowManager()
    window_size = 24
    train_x = create_x_input(glider_to_train)
    x_train, y_train = data_window_manager.generate_window(window_size, train_x, glider_to_train.ocean.temperature_c)
    model_manager.train(x_train[:-1], y_train[1:])
    return (predict_windowed(glider_drifted_22, model_manager, prediction_names[0], titles[0], png_filenames[0],
                             data_window_manager, window_size)), (
        predict_windowed(glider_to_predict, model_manager, prediction_names[1], titles[1], png_filenames[1],
                         data_window_manager, window_size))


def predict_windowed(glider_to_predict: WaveGliderV2, model_manager: ModelManager, prediction_name: str, title: str,
                     png_filename: str, data_window_manager: DataWindowManager, window_size: int):
    x_test = create_x_input(glider_to_predict)
    x_test, y_test = data_window_manager.generate_window(window_size, x_test,
                                                         glider_to_predict.ocean.temperature_c)
    results_windows = model_manager.predict(x_test[:-1], y_test[1:])
    results = {k: data_window_manager.reverse_windows(result) for k, result in results_windows.items()}
    ticks = ([glider_to_predict.ocean.timestamp[window_size:len(list(results.values())[0].y_pred) + window_size]]
             * len(model_manager.models))
    graph_model_results(results, title, ticks, png_filename)
    return get_table_results(results, prediction_name)


def predict_windowed_splitted(glider_to_predict: WaveGliderV2, model_manager: ModelManager, prediction_name: str,
                              title: str,
                              png_filename: str, data_window_manager: DataWindowManager, window_size: int,
                              train_percent: float):
    x_test = create_x_input(glider_to_predict)
    train_split_idx = round(len(glider_to_predict.weather.temperature_c) * train_percent)
    x_test, y_test = data_window_manager.generate_window(window_size,
                                                         x_test[
                                                         train_split_idx:],
                                                         glider_to_predict.ocean.temperature_c[
                                                         train_split_idx:])
    results_windows = model_manager.predict(x_test[:-1], y_test[1:])
    results = {k: data_window_manager.reverse_windows(result) for k, result in results_windows.items()}
    ticks = ([glider_to_predict.ocean.timestamp
             [window_size + train_split_idx: len(list(results.values())[0].y_pred) + train_split_idx + window_size]]
             * len(model_manager.models))
    graph_model_results(results, title, ticks,
                        png_filename)
    return get_table_results(results, prediction_name)


def create_plot_param(model_name: str, result: PredictorResult, label_1: str, label_2: str, x: list) -> (PlotStylishParams, PlotStylishParams):
    return (PlotStylishParams(BasicPlotParams(x, result.y_true, model_name),
                              MarkerParams("coral", label_1,
                                           "-", 1),
                              get_limited_plot_params(x, result.y_true)),
            PlotStylishParams(BasicPlotParams(x, result.y_pred, model_name),
                              MarkerParams("darkolivegreen", label_2,
                                           "dotted", 1),
                              get_limited_plot_params(x, result.y_pred))
            )


def create_predicted_params(models_results, x: list) -> [(PlotStylishParams, PlotStylishParams)]:
    result = []
    model_name, model_result = list(models_results.items())[0]
    result.append(create_plot_param(model_name, model_result,
                                    "Temperatura de la \n superficie del mar",
                                    "Temperatura predicha", x))
    result.extend(list(map(lambda result: create_plot_param(result[0], result[1], "", "", x),
                           list(models_results.items())[1:])))
    return result


def graph_model_results(results: dict[str, PredictorResult], title: str, x_ticks: list, filename: str) -> None:
    params = create_predicted_params(results, list(range(len(x_ticks[0]))))
    chart_creator = MatplotlibFigureCreator(len(params), 1, (10, 10), 12, 12)
    chart_creator.create_correlations(params, [], title, x_ticks)
    MatplotlibFigureStorer().store(RESULT_DIR + filename)


def calculate_min_lim(value_list: list[float]) -> float:
    return min(value_list) - 0.01 * min(value_list)


def calculate_max_lim(value_list: list[float]) -> float:
    return max(value_list) + 0.01 * max(value_list)


def get_limited_plot_params(x: list, y: list) -> LimitedPlotArea:
    return LimitedPlotArea(min(x), max(x), calculate_min_lim(y), calculate_max_lim(y))


def get_table_results(results, row_idx: str) -> Table:
    columns = list(map(lambda model_name: Table.Column(model_name, [results[model_name].error]), results))
    return Table(columns, [row_idx + " MSE error"])



main()
