
import { interpreters } from 'yoastseo';

export default class ResultContainers {
  /**
   * Controller of Yoast results
   *
   * @param {Result} results Results of yoastseo module
   */
  constructor(results) {
    this.results = results;
    this.readabilityContainer = $('#yoast_results_readability');
    this.seoContainer = $('#yoast_results_seo');
  }

  /**
   * Clear Results
   *
   * @param {object} $container Jquery selector of the container
   * @returns {void}
   */
  static clear($container) {
    const $success = $container.find('.success');
    const $medium = $container.find('.medium');
    const $errors = $container.find('.errors');
    $success.empty();
    $medium.empty();
    $errors.empty();
  }

  /**
   * Get HTML icon if success or error according to the score
   *
   * @param {AssessmentResult} result Assessment result of yoastseo module
   * @return {string}
   */
  static scoreIcon(result) {
    switch(interpreters.scoreToRating(result.score)) {
      case 'good':
        return '<i class="icon" aria-hidden="true">🟢</i>';
      case 'ok':
        return '<i class="icon" aria-hidden="true">🟡</i>';
      case 'bad':
        return '<i class="icon" aria-hidden="true">🔴</i>';
    }
  }

  /**
   * Get Jquery instance of success or errors container
   *
   * @param {object} $container Jquery selector of the container
   * @param {AssessmentResult} result Assessment result of yoastseo module
   * @return {object}
   */
  static getStatusContainer($container, result) {
    const $success = $container.find('.success');
    const $medium = $container.find('.medium');
    const $errors = $container.find('.errors');
    const rating = interpreters.scoreToRating(result.score);
    if (rating == 'good') {
      return $success;
     } else if (rating == 'ok') {
      return $medium
     } else {
      return $errors;
     }
  }

  /**
   * Add AssessmentResult object to the container
   *
   * @param {object} $container Jquery selector of the container
   * @param {AssessmentResult} result Assessment result of yoastseo module
   * @return {void}
   */
  static addResult($container, result) {
    if (result.score !== 0) {
      ResultContainers.getStatusContainer($container, result).append(
        `<li>${ResultContainers.scoreIcon(result)} ${result.text}</li>`,
      );
    }
  }

  /**
   * Synchronize the UI with results of yoastseo module
   *
   * @return {void}
   */
  sync() {
    // Clean containers
    ResultContainers.clear(this.readabilityContainer);
    ResultContainers.clear(this.seoContainer);

    // Append Data
    Array.prototype.forEach.call(this.results.result.readability.results, (el) => {
      ResultContainers.addResult(this.readabilityContainer, el);
    });
    Array.prototype.forEach.call(this.results.result.seo[''].results, (el) => {
      ResultContainers.addResult(this.seoContainer, el);
    });
  }
}
