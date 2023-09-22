from flask import render_template, session
from .. import AppConst
from ..models import Document

class DocumentNode:
    def __init__(self, document: Document):
        self.document = document
        self.children = []

    def add_child(self, child_node):
        """
        Add a document to the node.
        """
        self.children.append(child_node)

    def render_node(self) -> str:
        """
        Render a DocumentNode to HTML
        """
        return render_template("document_node.html", node=self, 
                               is_current=self.document.id==session[AppConst.SESSION_CURRENT_FOLDER_KEY])

    def to_dict(self):
        """
        Convert the tree to a dictionary representation.
        """
        result = {
            Document.Const.FIELD_ID: str(self.document.id),
            Document.Const.FIELD_TITLE: self.document.title,
        }
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        return result
    
class DocumentTree:
    def __init__(self, root_document=None):
        if root_document is None:
            self.root = None
        else:
            self.root = DocumentNode(root_document)

    def add_node(self, node: DocumentNode):
        """
        Add a document to the tree.
        """
        if self.root is None:
            self.root = node
        else:
            self._add_recursive(self.root, node)

    def _add_recursive(self, current_node, document_node):
        """
        Recursively add a document to the tree starting from a given node.
        """
        if current_node.document.id == document_node.document.mother:
            current_node.add_child(document_node)
        else:
            for child_node in current_node.children:
                self._add_node_recursive(child_node, document_node)

    def render_tree(self) -> str:
        """
        Render a DocumentTree to HTML
        """
        return self.root.render_node()

    def to_dict(self):
        """
        Convert the tree to a dictionary representation.
        """
        if self.root:
            return self.root.to_dict()
        else:
            return {}