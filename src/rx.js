class Observable {
}

class AnonymousObservable extends Observable {
  constructor(subscribe) {
    super();
    this.__subscribe = subscribe;
  }
  subscribe(onNext, onError, onCompleted) {
    this.__subscribe(onNext, onError, onCompleted);
  }
}

Observable.prototype.map = function(fn) {
  return new AnonymousObservable((onNext, onError, onCompleted) => {
    this.subscribe(value => {
      try {
        onNext(fn(value));
      } catch (e) {
        onError(e);
      }
    }, onError, onCompleted);
  });
};

Observable.prototype.debounce = function(dueTime) {
  return new AnonymousObservable((onNext, onError, onCompleted) => {
    let timerId = null;
    const cancel = () => {
      if (timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
    };
    this.subscribe(value => {
      cancel();
      timerId = setTimeout(() => {
        timerId = null;
        onNext(value);
      }, dueTime);
    }, err => {
      cancel();
      onError(err);
    }, () => {
      cancel();
      onCompleted();
    });
  });
};

Observable.prototype.startWith = function() {
    const args = Array.prototype.slice.call(arguments);
    return new AnonymousObservable((onNext, onError, onCompleted) => {
        args.forEach(onNext);
        this.subscribe(onNext, onError, onCompleted);
    });
};

const noOp = () => {};

export class Subject extends Observable {
  constructor() {
    super();
    this.observers = [];
  }
  subscribe(onNext, onError, onCompleted) {
    this.observers.push({
      onNext: onNext || noOp,
      onError: onError || noOp,
      onCompleted: onCompleted || noOp
    });
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
