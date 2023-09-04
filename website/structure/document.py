from ..models import Document

class DocumentNode:
    def __init__(self, document: Document):
        self.document = document
        self.children = []

    def add_child(self, child_document: Document):
        """
        Add a document to the node.
        """
        child_node = DocumentNode(child_document)
        self.children.append(child_node)

    def render_node(self) -> str:
        """
        Render a DocumentNode to HTML
        """
        html = f"<ul>"
        html += f"<li>{self.document.title}</li>"
        for child in self.children:
            html += f"<li>{child.render_node()}</li>"
        html += f"</ul>"
        return html

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

    def add_node(self, document: Document):
        """
        Add a document to the tree.
        """
        if self.root is None:
            self.root = DocumentNode(document)
        else:
            self._add_recursive(self.root, document)

    def _add_recursive(self, current_node, document):
        """
        Recursively add a document to the tree starting from a given node.
        """
        if current_node.document[Document.Const.FIELD_ID] == document[Document.Const.FIELD_MOTHER]:
            current_node.add_child(document)
        else:
            for child_node in current_node.children:
                self._add_node_recursive(child_node, document)

    def render_tree(self) -> str:
        """
        Render a DocumentTree to HTML
        """
        return f"{self.root.render_node()}"

    def to_dict(self):
        """
        Convert the tree to a dictionary representation.
        """
        if self.root:
            return self.root.to_dict()
        else:
            return {}