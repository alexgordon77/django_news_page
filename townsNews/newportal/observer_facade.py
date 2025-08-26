from newportal.builder import NewsBlockBuilder, OneArticleBlockBuilder
from newportal.observer import ObserverTxtError, ObserverUserActivity, ObserverAuthorActivity, \
    ObserverPopularArticleTracker, ObserverArticleSaveTracker, ObserverProhibitedWords, ObserverNewTag, \
    ObserverSeoTitleChecker, ObserverArticleCount, ObserverBlockCreationTime, ObserverJsonError


# OBSERVER FACADE ERROR
class ObserverFacadeError:
    def __init__(self, builder: NewsBlockBuilder = None) -> None:
        self.builder = builder or OneArticleBlockBuilder()
        self.observers = []

    def attach_observers(self) -> None:
        self.observers = [
            ObserverTxtError(),
            ObserverJsonError(),
        ]
        for observer in self.observers:
            self.builder.attach_observer(observer)

    def notify_observers(self) -> None:
        self.builder.notify_observers()


# OBSERVER FACADE ACTIVITY
class ObserverFacadeActivity:
    def __init__(self, builder: NewsBlockBuilder = None) -> None:
        self.builder = builder or OneArticleBlockBuilder()
        self.observers = []

    def attach_observers(self) -> None:
        self.observers = [
            ObserverUserActivity(),
            ObserverAuthorActivity(),
        ]
        for observer in self.observers:
            self.builder.attach_observer(observer)

    def notify_observers(self) -> None:
        self.builder.notify_observers()


# OBSERVER FACADE TRACKER
class ObserverFacadeTracker:
    def __init__(self, builder: NewsBlockBuilder = None) -> None:
        self.builder = builder or OneArticleBlockBuilder()
        self.observers = []

    def attach_observers(self) -> None:
        self.observers = [
            ObserverPopularArticleTracker(),
            ObserverArticleSaveTracker(),
        ]
        for observer in self.observers:
            self.builder.attach_observer(observer)

    def notify_observers(self) -> None:
        self.builder.notify_observers()


# OBSERVER FACADE WORDS
class ObserverFacadeWord:
    def __init__(self, builder: NewsBlockBuilder = None) -> None:
        self.builder = builder or OneArticleBlockBuilder()
        self.observers = []

    def attach_observers(self) -> None:
        self.observers = [
            ObserverNewTag(),
            ObserverProhibitedWords(["заборонене слово"]),
            ObserverSeoTitleChecker(),
        ]
        for observer in self.observers:
            self.builder.attach_observer(observer)

    def notify_observers(self) -> None:
        self.builder.notify_observers()


# OBSERVER FACADE COUNT
class ObserverFacadeCount:
    def __init__(self, builder: NewsBlockBuilder = None) -> None:
        self.builder = builder or OneArticleBlockBuilder()
        self.observers = []

    def attach_observers(self) -> None:
        self.observers = [
            ObserverArticleCount(),
            ObserverBlockCreationTime(),
        ]
        for observer in self.observers:
            self.builder.attach_observer(observer)

    def notify_observers(self) -> None:
        self.builder.notify_observers()
