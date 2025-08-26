import time
from abc import ABC, abstractmethod
import json
from django.contrib import messages
from newportal.models import Tag
from typing import List


# OBSERVER
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        pass

    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class NewsBlockSubject(Subject):
    def __init__(self, block, request=None):
        self._observers: List['Observer'] = []
        self._block = block
        self.request = request

    def attach(self, observer: 'Observer') -> None:
        self._observers.append(observer)

    def detach(self, observer: 'Observer') -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def get_block(self):
        return self._block


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass


# Спостерігач для помилок у текстовому файлі
class ObserverTxtError(Observer):
    def update(self, subject: NewsBlockSubject) -> None:
        try:
            block = subject.get_block()

            if not isinstance(block, dict):
                raise TypeError("Очікувався словник, отримано: {}".format(type(block)))

            if 'one_article_block' not in block:
                self.log_error_to_txt("Відсутній блок: Блок з однією статтею")
            if 'two_articles_block' not in block:
                self.log_error_to_txt("Відсутній блок: Блок з двома статтями")
            if 'three_articles_block' not in block:
                self.log_error_to_txt("Відсутній блок: Блок з трьома статтями")
            if 'six_articles_block' not in block:
                self.log_error_to_txt("Відсутній блок: Блок з шістьма статтями")

        except Exception as e:
            self.log_error_to_txt(f"Error: {type(e).__name__}: {str(e)}")

    def log_error_to_txt(self, message: str) -> None:
        with open('errors.txt', 'a') as file:
            file.write(message + '\n')


# Спостерігач для помилок у JSON файлі
class ObserverJsonError(Observer):
    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()
        missing_blocks = []

        if 'one_article_block' not in block:
            missing_blocks.append('Блок з однією статтею')
        if 'two_articles_block' not in block:
            missing_blocks.append('Блок з двома статтями')
        if 'three_articles_block' not in block:
            missing_blocks.append('Блок з трьома статтями')
        if 'six_articles_block' not in block:
            missing_blocks.append('Блок з шістьма статтями')

        if missing_blocks:
            message = f"Помилки: {', '.join(missing_blocks)} не знайдено"
            self.log_error_to_json(message)

    def log_error_to_json(self, message: str) -> None:
        error_data = {'error': message}
        with open('errors.json', 'a') as file:
            json.dump(error_data, file)
            file.write('\n')


# Спостерігач, що повідомляє користувача про оновлення/додавання статей
class ObserverArticleCount(Observer):
    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()

        if 'one_article_block' in block:
            count = 1
        elif 'two_articles_block' in block:
            count = 2
        elif 'three_articles_block' in block:
            count = 3
        elif 'six_articles_block' in block:
            count = 6
        else:
            count = 0

        message = f"Новини оновлено: додано {count} статей."
        if subject.request:
            self.notify_user(subject.request, message)

    def notify_user(self, request, message):
        messages.info(request, message)


# Спостерігач, що відслідковує час створення блоку новин
class ObserverBlockCreationTime(Observer):
    def __init__(self):
        self.start_time = time.time()
        self.creation_logs = []
        self.creation_logs_file = 'creation_times.txt'

    def update(self, subject: NewsBlockSubject) -> None:
        end_time = time.time()
        creation_time = end_time - self.start_time
        block_type = subject.get_block()
        log_entry = f"{block_type}: {creation_time:.2f}"
        self.append_creation_log(log_entry)
        self.start_time = time.time()

    def append_creation_log(self, log_entry: str) -> None:
        with open(self.creation_logs_file, 'a') as file:
            file.write(log_entry + '\n')


# Спостерігач, що відслідковує появу нового тегу
class ObserverNewTag(Observer):
    def __init__(self):
        self.existing_tags = set(Tag.objects.values_list('name', flat=True))

    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()
        new_tags = self.find_new_tags(block)
        if new_tags:
            self.log_to_file(f"Нові теги: {', '.join(new_tags)}")

    def find_new_tags(self, block: dict) -> List[str]:
        new_tags = set()

        for article_list in block.values():
            if isinstance(article_list, list):
                for article in article_list:
                    for tag in article.tags:
                        tag_name = tag.name
                        if tag_name not in self.existing_tags:
                            new_tags.add(tag_name)
                            self.existing_tags.add(tag_name)
            else:
                for tag in article_list.tags:
                    tag_name = tag.name
                    if tag_name not in self.existing_tags:
                        new_tags.add(tag_name)
                        self.existing_tags.add(tag_name)

        return list(new_tags)

    def log_to_file(self, message: str) -> None:
        with open('new_tags.log', 'a') as file:
            file.write(message + '\n')


# Спостерігач для перевірки контенту новин на заборонені слова
class ObserverProhibitedWords(Observer):
    def __init__(self, prohibited_words: List[str]):
        self.prohibited_words = prohibited_words

    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()
        violations = self.check_prohibited_words(block)
        if violations:
            self.log_to_file(f"Знайдено заборонені слова: {', '.join(violations)}")

    def check_prohibited_words(self, block: dict) -> List[str]:
        violations = []
        for article in block.values():
            content = getattr(article, 'content', '').lower()
            for word in self.prohibited_words:
                if word in content:
                    violations.append(f"{getattr(article, 'title', 'No Title')}: {word}")
        return violations

    def log_to_file(self, message: str) -> None:
        with open('prohibited_words.log', 'a') as file:
            file.write(message + '\n')


# Спостерігач для аналізу активності користувачів, які блоки новин переглядали користувачі
class ObserverUserActivity(Observer):
    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()
        user = subject.request.user if subject.request and subject.request.user.is_authenticated else 'Anonymous'
        self.log_to_file(f"Користувач {user} переглянув блок новин.")

    def log_to_file(self, message: str) -> None:
        with open('user_activity.log', 'a') as file:
            file.write(message + '\n')


# Спостерігач для моніторингу популярних статей
class ObserverPopularArticleTracker(Observer):
    def __init__(self):
        self.article_views = {}

    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()

        for article_list in block.values():
            if isinstance(article_list, list):
                for article in article_list:
                    article_id = article.id
                    self.article_views[article_id] = self.article_views.get(article_id, 0) + 1
            else:
                article_id = article_list.id
                self.article_views[article_id] = self.article_views.get(article_id, 0) + 1

        self.log_to_file(f"Популярні статті: {self.article_views}")

    def log_to_file(self, message: str) -> None:
        with open('popular_articles.log', 'a') as file:
            file.write(message + '\n')


# Спостерігач відстежує, скільки статей опублікував кожен автор
class ObserverAuthorActivity(Observer):
    def __init__(self):
        self.author_articles = {}

    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()

        for article_list in block.values():
            if isinstance(article_list, list):
                for article in article_list:
                    author = article.author.name if article.author else 'Unknown Author'
                    self.author_articles[author] = self.author_articles.get(author, 0) + 1
            else:
                author = article_list.author.name if article_list.author else 'Unknown Author'
                self.author_articles[author] = self.author_articles.get(author, 0) + 1

        self.log_to_file(f"Активність авторів: {self.author_articles}")

    def log_to_file(self, message: str) -> None:
        with open('author_activity.log', 'a') as file:
            file.write(message + '\n')


# Спостерігач для перевірки заголовків на SEO
class ObserverSeoTitleChecker(Observer):
    def __init__(self, min_length=50, max_length=60):
        self.min_length = min_length
        self.max_length = max_length

    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()

        for article_list in block.values():
            if isinstance(article_list, list):
                for article in article_list:
                    title = article.title
                    if len(title) < self.min_length or len(title) > self.max_length:
                        self.log_to_file(f"Заголовок '{title}' не відповідає SEO-правилам.")
            else:
                title = article_list.title
                if len(title) < self.min_length or len(title) > self.max_length:
                    self.log_to_file(f"Заголовок '{title}' не відповідає SEO-правилам.")

    def log_to_file(self, message: str) -> None:
        with open('seo_title_issues.log', 'a') as file:
            file.write(message + '\n')


# Спостерігач для відстеження збереження статей користувачами
class ObserverArticleSaveTracker(Observer):
    def update(self, subject: NewsBlockSubject) -> None:
        block = subject.get_block()

        for article_list in block.values():
            if isinstance(article_list, list):
                for article in article_list:
                    save_count = article.num_saves
                    if save_count > 0:
                        self.log_to_file(f"Статтю '{article.title}' зберегли {save_count} разів.")
            else:
                save_count = article_list.num_saves
                if save_count > 0:
                    self.log_to_file(f"Статтю '{article_list.title}' зберегли {save_count} разів.")

    def log_to_file(self, message: str) -> None:
        with open('article_saves.log', 'a') as file:
            file.write(message + '\n')