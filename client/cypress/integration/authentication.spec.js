describe("Authentication", function () {
  it("Can log in", function () {
    cy.visit("/#/log-in");
    cy.get("input#username").type("hey@example.com");
    cy.get("input#password").type("pAssw0rd", { log: false });
    cy.get("button").contains("Log in").click();
    cy.hash().should("eq", "#/");
  });

  it("Can sign up", function () {
    cy.visit("/#/sign-up");
    cy.get("input#username").type("hey@example.com");
    cy.get("input#firstName").type("Hey");
    cy.get("input#lastName").type("Hey");
    cy.get("input#password").type("pAssw0rd", { log: false });
    cy.get("select#group").type("driver");
    cy.fixture("images/photo.jpg").then((photo) => {
      cy.get("input#photo").attachFile("images/photo.jpg");
    });
    cy.get("button").contains("Sign up").click();
    cy.hash().should("eq", "#/log-in");
  });
});
