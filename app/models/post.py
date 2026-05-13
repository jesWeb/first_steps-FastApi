
class PostORM(Base):
    # decalrar tabla
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)
    # declarar columnas
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    """Relacion uno a nuno """
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional["AuthorORM"]] = relationship(
        back_populates="posts")

    """Relacion muchos a muchos """
    tags: Mapped[List["TagOrm"]] = relationship(
        # realcion con la tabla intermedia
        secondary=post_tags,
        # accede atravez alias
        back_populates="posts",
        # busqueda
        lazy="selectin",
        # borrado cascada
        passive_deletes=True
    )
