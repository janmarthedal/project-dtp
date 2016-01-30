const noOp = () => {};

class Observable {
  constructor() {
    this.observers = [];
  }
  forEach(onNext, onError, onCompleted) {
    this.observers.push({
      onNext: onNext || noOp,
      onError: onError || noOp,
      onCompleted: onCompleted || noOp
    });
  }
}

class ChainObservable extends Observable {
  constructor(obsSetup) {
    super();
    obsSetup({
      onNext: value => {
        this.observers.slice().forEach(obs => obs.onNext(value));
      },
      onError: err => {
        this.observers.slice().forEach(obs => obs.onError(err));
      },
      onCompleted: () => {
        this.observers.slice().forEach(obs => obs.onCompleted());
      }
    });
  }
}

Observable.prototype.map = function(fn) {
  return new ChainObservable(obs => {
    this.forEach(value => {
      try {
        obs.onNext(fn(value));
      } catch (e) {
        obs.onError(e);
      }
    }, err => {
      obs.onError(err);
    }, () => {
      obs.onCompleted();
    });
  });
};

Observable.prototype.debounce = function(dueTime) {
  return new ChainObservable(obs => {
    let timerId = null;
    const cancel = () => {
      if (timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
    }
    this.forEach(value => {
      cancel();
      timerId = setTimeout(() => {
        timerId = null;
        obs.onNext(value);
      }, dueTime);
    }, err => {
      cancel();
      obs.onError(err);
    }, () => {
      cancel();
      obs.onCompleted();
    });
  });
};

export class Subject extends Observable {
  constructor() {
    super();
  }
  onNext(value) {
    this.observers.slice().forEach(obs => obs.onNext(value));
  }
  onError(err) {
    this.observers.slice().forEach(obs => obs.onError(err));
  }
  onCompleted() {
    this.observers.slice().forEach(obs => obs.onCompleted());
  }
}
