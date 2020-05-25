from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms.formsets import DELETION_FIELD_NAME

from quiz.models import *


class QuestionForm(forms.Form):
    answers = forms.ChoiceField(widget=forms.RadioSelect(), label=u"Please select an answer:")

    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.question = question.question
        answers = question.choices.order_by('weight').all()
        self.fields['answers'].choices = [(i, a.content) for i, a in enumerate(answers)]
        for pos, answer in enumerate(answers):
            if answer.id == question.correct_answer.id:
                self.correct = pos
                break

    def is_correct(self):
        if not self.is_valid():
            return False
        return self.cleaned_data['answers'] == str(self.correct)


def quiz_forms(quiz, data=None):
    questions = Question.objects.filter(quiz=quiz).order_by('id')
    form_list = []
    for pos, question in enumerate(questions):
        form_list.append(QuestionForm(question, data, prefix=pos))
    return form_list


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'slug', 'summary', 'category', 'status']


AnswerFormset = inlineformset_factory(Question, Answer, extra=0, min_num=1, fields=['question', 'content', 'weight', 'correct'])


class BaseQuestionFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BaseQuestionFormset, self).add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = 'Delete question'
        # save the formset in the 'nested' property
        form.nested = AnswerFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='answer-%s-%s' % (
                form.prefix,
                AnswerFormset.get_default_prefix()),
            )

    def is_valid(self):
        result = super(BaseQuestionFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super(BaseQuestionFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result


QuestionFormset = inlineformset_factory(Quiz,
                                        Question,
                                        formset=BaseQuestionFormset,
                                        extra=0,
                                        min_num=1,
                                        fields='__all__')
