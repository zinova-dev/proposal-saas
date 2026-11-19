'use client';

/**
 * Browser translation and some extensions rewrite text nodes outside of React.
 * When React later tries to remove or move a node that is no longer a child of
 * the expected parent, the DOM throws and the whole page unmounts.
 * These guards skip the operation instead of crashing.
 */
if (typeof window !== 'undefined' && !(window as { __domGuarded?: boolean }).__domGuarded) {
  (window as { __domGuarded?: boolean }).__domGuarded = true;

  const originalRemoveChild = Node.prototype.removeChild;
  Node.prototype.removeChild = function <T extends Node>(this: Node, child: T): T {
    if (child.parentNode !== this) {
      return child;
    }
    return originalRemoveChild.call(this, child) as T;
  };

  const originalInsertBefore = Node.prototype.insertBefore;
  Node.prototype.insertBefore = function <T extends Node>(
    this: Node,
    newNode: T,
    referenceNode: Node | null
  ): T {
    if (referenceNode && referenceNode.parentNode !== this) {
      return newNode;
    }
    return originalInsertBefore.call(this, newNode, referenceNode) as T;
  };
}

export function DomSafeguard() {
  return null;
}
