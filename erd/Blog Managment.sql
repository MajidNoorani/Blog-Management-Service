CREATE TABLE "Comment" (
  "id" serial,
  "postId" integer NOT NULL,
  "userId" integer NOT NULL,
  "parentId" integer,
  "comment" varchar(255) NOT NULL,
  "likeCount" integer NOT NULL,
  "disLikeCount" integer NOT NULL,
  PRIMARY KEY ("id")
);
COMMENT ON COLUMN "Comment"."parentId" IS 'CommentId';

CREATE TABLE "CommentReaction" (
  "id" serial,
  "commentId" integer NOT NULL,
  "userId" integer NOT NULL,
  "reactionType" varchar(7) NOT NULL,
  PRIMARY KEY ("id")
);
COMMENT ON COLUMN "CommentReaction"."reactionType" IS '"Like" , "disLike"';

CREATE TABLE "Post" (
  "id" serial,
  "title" varchar(100) NOT NULL,
  "content" text NOT NULL,
  "postCategoryId" integer NOT NULL,
  "image" varchar(255) NOT NULL,
  "AuthorName" varchar(100) NOT NULL,
  "Tags" varchar[],
  "postStatus" poststatus NOT NULL,
  "postPublishDate" timestamptz,
  "postArchivedDate" timestamptz,
  "reviewStatus" reviewstatus,
  "reviewResponseDate" timestamptz,
  "isExternalSource" bool NOT NULL,
  "externalLink" varchar(255),
  "commentsEnabled" bool NOT NULL,
  "metaDescription" varchar(255),
  "seoKeywords" varchar [],
  "readTime" integer NOT NULL,
  "excerpt" varchar(255) NOT NULL,
  "relatedPosts" integer [],
  "createdDate" timestamptz NOT NULL,
  "createdBy" integer NOT NULL,
  "updatedDate" timestamptz NOT NULL,
  "updatedBy" integer NOT NULL,
  PRIMARY KEY ("id")
);
COMMENT ON COLUMN "Post"."postCategoryId" IS 'Indicates the category or topic of the blog post (e.g., Technology, Lifestyle, Travel)';
COMMENT ON COLUMN "Post"."AuthorName" IS 'userId';
COMMENT ON COLUMN "Post"."postStatus" IS 'Indicates the status of the blog post 
Enumeration (Draft, Publish, Archive)
New => Draft , Publish
Draft => Publish
Publish => Archive';
COMMENT ON COLUMN "Post"."postPublishDate" IS 'Records the date when the blog post was published.
';
COMMENT ON COLUMN "Post"."postArchivedDate" IS 'Records the date when the blog post was archived or removed from the active list of posts';
COMMENT ON COLUMN "Post"."reviewStatus" IS 'Indicates the publication status of the blog post 

Enumeration (Pending , Accept, Reject)
If PostStatus != Publish => reviewStatus is NULL
If PostStatus  = Publish => reviewStatus
New => Pending
Pending => Accept
Pending => Reject
';
COMMENT ON COLUMN "Post"."externalLink" IS 'Provides an option to include an external link within the blog post, directing users to additional resources or related content';
COMMENT ON COLUMN "Post"."commentsEnabled" IS 'Indicates whether comments are allowed on the blog post, providing flexibility for content creators to manage engagement settings';
COMMENT ON COLUMN "Post"."metaDescription" IS 'Stores a brief summary or description of the blog post, typically used for SEO purposes and displayed in search engine results.
';
COMMENT ON COLUMN "Post"."seoKeywords" IS 'Stores a list of keywords relevant to the blog post, aiding in search engine optimization efforts.
';
COMMENT ON COLUMN "Post"."readTime" IS ' Estimates the time required to read the blog post';
COMMENT ON COLUMN "Post"."excerpt" IS 'Provides a short summary or teaser of the blog post, displayed on archive pages or in search results.
';
COMMENT ON COLUMN "Post"."relatedPosts" IS 'Stores references to related or similar blog posts, enhancing content discoverability and user engagement.
';

CREATE TABLE "PostCategory" (
  "id" serial,
  "parentPostCategoryId" integer NOT NULL,
  "title" varchar(100) NOT NULL,
  "description" varchar(255),
  "imageURL" varchar(255),
  "status" categorystatus NOT NULL,
  "createdDate" timestamptz NOT NULL,
  "createdBy" integer NOT NULL,
  "updatedDate" timestamptz NOT NULL,
  "updatedBy" integer NOT NULL,
  PRIMARY KEY ("id")
);
COMMENT ON COLUMN "PostCategory"."status" IS 'Indicates the status of the category 
Enumeration (Active, Inactive, Archived)';

CREATE TABLE "PostDetail" (
  "id" serial,
  "postId" integer NOT NULL,
  "viewCount" integer,
  "likeCount" integer,
  "socialShareCount" integer,
  "ratingCount" integer,
  "averageRating" numeric(1, 1),
  "commentCount" integer,
  "createdDate" timestamptz NOT NULL,
  "createdBy" integer NOT NULL,
  "updatedDate" timestamptz NOT NULL,
  "updatedBy" integer NOT NULL,
  PRIMARY KEY ("id")
);
COMMENT ON COLUMN "PostDetail"."viewCount" IS 'Tracks the number of views or visits the blog post has received';
COMMENT ON COLUMN "PostDetail"."likeCount" IS 'Records the number of likes or thumbs-up the blog post has received';
COMMENT ON COLUMN "PostDetail"."socialShareCount" IS 'Tracks the number of times the blog post has been shared on social media platforms';
COMMENT ON COLUMN "PostDetail"."ratingCount" IS 'Tracks the number of user ratings received for the blog post';
COMMENT ON COLUMN "PostDetail"."averageRating" IS 'Calculates the average rating score based on user ratings, providing feedback on content quality';
COMMENT ON COLUMN "PostDetail"."commentCount" IS 'Counts the number of comments posted on the blog post, fostering community interaction and discussion';

CREATE TABLE "Rate" (
  "id" serial,
  "postId" integer NOT NULL,
  "userId" integer NOT NULL,
  "rate" integer NOT NULL,
  PRIMARY KEY ("id")
);
COMMENT ON COLUMN "Rate"."rate" IS '1,2,3,4,5';

ALTER TABLE "Comment" ADD CONSTRAINT "postId" FOREIGN KEY ("postId") REFERENCES "Post";
ALTER TABLE "Comment" ADD CONSTRAINT "parentId" FOREIGN KEY ("parentId") REFERENCES "Comment";
ALTER TABLE "CommentReaction" ADD CONSTRAINT "commentId" FOREIGN KEY ("commentId") REFERENCES "Comment";
ALTER TABLE "Post" ADD CONSTRAINT "blogCategoryId" FOREIGN KEY ("blogCategoryId") REFERENCES "PostCategory";
ALTER TABLE "PostCategory" ADD CONSTRAINT "parentCategoryId" FOREIGN KEY ("parentCategoryId") REFERENCES "PostCategory";
ALTER TABLE "PostDetail" ADD CONSTRAINT "postId" FOREIGN KEY ("postId") REFERENCES "Post";
ALTER TABLE "Rate" ADD CONSTRAINT "postId" FOREIGN KEY ("postId") REFERENCES "Post";

